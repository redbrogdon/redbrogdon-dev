# Pixel-Art Compositor & Multi-Display Occlusion Engine

This document specifies the rendering pipeline, procedural pixel-art drawing algorithms, and native macOS window/wallpaper management subsystems of **Brog City**.

---

## 1. Offscreen 2× Integer Supersampled Compositor

### 1.1 Coordinate Space & Resolution Scaling
- **Native Logical Canvas**: `1376.0 × 768.0` (`16:9` aspect ratio), matching the pixel grid of the 5 bundled archetype scenes (`px = 2.0` base block size).
- **Viewport Aspect Fill**: When painting into an arbitrary target size `(size.width, size.height)`:
  ```text
  scale   = max(size.width / 1376.0, size.height / 768.0)
  offsetX = floor((size.width - 1376.0 * scale) / 2.0)
  offsetY = floor((size.height - 768.0 * scale) / 2.0)
  ```
  The canvas translates by `(offsetX, offsetY)` and scales uniformly by `(scale, scale)`.
- **Offscreen Wallpaper Export Resolution**: `2752 × 1536` (`2×` exact integer multiple of `1376 × 768`). Rendering at `2752 × 1536` with nearest-neighbor sampling (`FilterQuality.none` and `isAntiAlias = false`) ensures macOS `WallpaperAgent` displays razor-sharp pixel blocks on Retina displays without bilinear blur.

### 1.2 Layer Compositing Order (`IntimateScenePainter.paint`)
Every frame / export composites up to 5 layers in strict back-to-front order:
1. **Base Scene Bitmap**: Draws `baseImage` stretched to `Rect(0, 0, 1376, 768)` with `isAntiAlias = false` and `filterQuality = FilterQuality.none`. If `baseImage` is `null` (e.g., while loading or in headless tests), fills `Rect(0, 0, 1376, 768)` with `0xFF0F172A`.
2. **Scene-Specific Dynamic Details**: Executed **only** when `isLiveGeminiImage == false` (bundled archetypes). Draws working analog clock hands, pulsing lantern halos, rising cup/chimney steam, drifting autumn leaves, water ripples, swimming fish, or hearth flames at exact architectural coordinates (see [schema.md](./schema.md#3-scene-specific-coordinate-geometry-1376--768-logical-canvas)).
3. **Weather & Atmosphere Layer (`_drawWeatherLayer`)**: Always drawn (even over live Gemini images, with reduced particle density so menu overrides have immediate visual feedback).
4. **Time-of-Day Ambient Lighting Tint (`_drawLightingTint`)**: Full-canvas blend rect per [schema.md](./schema.md#13-lightingmode).
5. **Optional Diagnostic HUD Badge (`_drawDiagnosticBadge`)**: Drawn at `(24, 44)` (`420 × 104`) when `showDiagnosticHud == true`.

---

## 2. Procedural Pixel-Art Drawing Primitives

All procedural primitives must be drawn with `isAntiAlias = false` using axis-aligned rectangles (`drawRect`) to preserve a strict pixel-art aesthetic.

### 2.1 Working Analog Clock Hands (`_drawPixelClockHands`)
- Computes angles from `lastUpdateTime`:
  ```text
  hour        = lastUpdateTime.hour % 12
  minute      = lastUpdateTime.minute
  minuteAngle = (minute / 60.0) * 2π - π/2
  hourAngle   = ((hour + minute / 60.0) / 12.0) * 2π - π/2
  ```
- **Hour Hand**: Endpoint `(cx + cos(hourAngle) * rx * 0.56, cy + sin(hourAngle) * ry * 0.56)`, drawn via `_drawPixelLine` with `pixelSize + 0.8`.
- **Minute Hand**: Endpoint `(cx + cos(minuteAngle) * rx * 0.84, cy + sin(minuteAngle) * ry * 0.84)`, drawn via `_drawPixelLine` with `pixelSize`.
- **Center Hub**: Square of size `hs = pixelSize * 1.6` centered at `(cx, cy)` in `hubColor`.
- **Stepped Line Algorithm (`_drawPixelLine`)**: Interpolates `steps = ceil(max(|dx|, |dy|))` points from `start` to `end`, rounding each sample `(px, py)` to integer coordinates and drawing a centered `pixelSize × pixelSize` rectangle.

### 2.2 Two-Tier Stepped Pixel Glow (`_drawPixelGlow`)
- Iterates a 2D grid `(dx, dy)` from `-radius` to `+radius` in increments of `step = 4.0`.
- For each cell where `dx² + dy² <= (radius * 0.5)²`, draws a `4 × 4` block with `color` (inner core).
- For each cell where `(radius * 0.5)² < dx² + dy² <= radius²`, draws a `4 × 4` block with `color` at `45%` of its original alpha (`color.a * 0.45`, outer halo).

### 2.3 Sinusoidal Pixel Steam / Smoke (`_drawPixelSteam`)
- Renders `puffs = 5` ascending square blocks (`i = 0..4`, `progress = (i + 1) / 5`):
  ```text
  driftX = sin(progress * π + seed * 0.4) * (4.0 + i * 1.8) + (rng.nextDouble() - 0.5) * 3.0
  px     = round(origin.dx + driftX)
  py     = round(origin.dy - progress * height)
  size   = round(3.0 + i * 1.4)
  alpha  = color.a * (1.0 - progress * 0.65)
  ```

### 2.4 Multi-Layer Weather Particle Systems (`_drawWeatherLayer`)
Seeded deterministically per frame with `rng = Random(2026 + updateCount * 41 + weather.index * 97)`:
- **`rain`**:
  1. Full-canvas wash `0x301E293B` (skipped if `isLiveGeminiImage`).
  2. Diagonal rain streaks (`dropCount = 85` if `isLiveGeminiImage`, else `210`): Every 3rd drop (`i % 3 == 0`) is a foreground streak (`6` segments, `2.5 × 4.5` px each, `0xBBBAE6FD`); others are background streaks (`4` segments, `2.0 × 4.5` px each, `0x6690CAF9`). Each segment `s` offsets by `(-s * 2.0, +s * 4.5)`.
  3. Ground/water splashes (`42` splashes across `x ∈ [40, 1336)`, `y ∈ [440, 748)` in `0xAABAE6FD`): base bar `(sx - 4, sy, 10, 2)` plus two crown pixels `(sx - 2, sy - 2, 2, 2)` and `(sx + 2, sy - 2, 2, 2)`.
- **`snow`**:
  1. Full-canvas frost wash `0x26E0F2FE` (skipped if `isLiveGeminiImage`).
  2. Snowflakes (`flakeCount = 80` if `isLiveGeminiImage`, else `185`):
     - `i % 6 == 0`: `6 × 6` crystal cross (`2 × 6` vertical + `6 × 2` horizontal in `0xEEFFFFFF`).
     - `i % 2 == 0`: `4 × 4` flake in `0xEEFFFFFF`.
     - Odd indices: `2.5 × 2.5` soft flake in `0x99E2E8F0`.
- **`mist`**:
  1. Full-canvas silver wash `0x2ECBD5E1` (skipped if `isLiveGeminiImage`).
  2. Layered horizontal fog banks (`bankCount = 14` if `isLiveGeminiImage`, else `28`): Each bank at `x ∈ [-40, 1156)`, `y ∈ [180, 720)`, width `mw ∈ [220, 540)` draws a core `mw × 14` bar (`0x40E2E8F0`) flanked by upper `(mx + 28, my - 8, mw - 56, 8)` and lower `(mx + 44, my + 14, mw - 88, 8)` bars (`0x28F8FAFC`).
- **`clear`**:
  1. If `!isLiveGeminiImage`, 4 diagonal warm sunbeams (`startX = 180 + b * 290`, `36` steps of `(startX + step * 8, step * 18, 48, 18)` in `0x14FFE082`).
  2. `36` glowing dust motes / fireflies across the canvas: `8 × 8` outer glow (`0x44FFB300`) with `4 × 4` core (`0xBBFFF59D`).

### 2.5 Diagnostic HUD Badge (`_drawDiagnosticBadge`)
When `showDiagnosticHud == true`, draws an overlay box at `(24, 44)` of size `420 × 104`:
- Background fill: `0xD80F172A`, top `2px` accent bar: `0xFF38BDF8`.
- 4 lines of `Menlo` Bold text:
  1. `BROG CITY • <SCENE TITLE UPPERCASE>` (`10pt`, `0xFF38BDF8`) at `(+12, +10)`
  2. `UPDATE #0001  •  LAST: HH:MM:SS  •  NEXT: HH:MM:SS | PAUSED | NEVER` (`11pt`, `0xFFFFFFFF`) at `(+12, +30)`
  3. `TRIGGER: <REASON>  •  WEATHER: <WEATHER>  •  LIGHT: <LIGHTING_ID>` (`9.5pt`, `0xFF94A3B8`) at `(+12, +50)`
  4. `<GEMINI STATUS UPPERCASE>` (`9.5pt`, `0xFF4ADE80` if `isLiveGeminiImage` else `0xFFFBBF24`) at `(+12, +70)`

### 2.6 Phase 1 Calibration Painter (`PixelTestCardPainter`)
Included in `lib/renderer/pixel_test_card_painter.dart` as a standalone diagnostic renderer (`virtualHeight = 450.0`) that cycles through 6 retro synth/harbor palettes (`DAWN AMBER`, `DAYLIGHT HARBOR`, `SUNSET SYNTH`, `MIDNIGHT NEON`, `EMERALD CYBER`, `TWILIGHT VIOLET`), steps a celestial orb across 12 arc positions, renders a `5 × 5` `2:1` isometric test island (`24 × 12` diamond tiles), corner calibration markers, and a central 12-slot HUD card.

---

## 3. Native macOS Window Lifecycle & Multi-Display Wallpaper Engine

### 3.1 Invisible 16×16 Metal Keeper Window vs. Interactive Preview Window
In macOS (`MainFlutterWindow.swift`), closing or hiding the window must **never** destroy the UI view controller or halt the GPU rasterizer:
- **Background Menu Bar Mode (Default on Launch, `isPreviewWindowVisible = false`)**:
  - `NSApp.setActivationPolicy(.accessory)` (hides Dock icon).
  - Window is configured as `.borderless`, `level = CGWindowLevelForKey(.desktopWindow)`, `collectionBehavior = [.canJoinAllSpaces, .stationary, .ignoresCycle]`, `ignoresMouseEvents = true`, `hasShadow = false`, `isOpaque = false`, `alphaValue = 0.0`, frame `NSRect(x: 0, y: 0, width: 16, height: 16)`, and ordered to the back. This keeps the Metal surface alive for offscreen `Picture.toImage(2752, 1536)` rasterization at near-zero GPU/CPU cost.
- **Interactive Preview Window Mode (`isPreviewWindowVisible = true`)**:
  - `NSApp.setActivationPolicy(.regular)`.
  - Restores `.titled, .closable, .miniaturizable, .resizable`, `.normal` level, `alphaValue = 1.0`, title `"Brog City — Preview Window"`, and centers a `min(1120, screenWidth * 0.78) × min(680, screenHeight * 0.78)` window.
  - Intercepts `windowShouldClose` to hide the preview window and return to background `.accessory` mode rather(than terminating the app).

### 3.2 Atomic Multi-Display Wallpaper Application
When `applyWallpaperPng` is invoked:
1. Resolves directory `~/Library/Application Support/brog_city/wallpapers/`.
2. Writes the PNG atomically to a unique filename:
   ```text
   brog_city_wallpaper_<updateCount>_<unixTimestampSeconds>.png
   ```
   *(Unique filenames are mandatory because macOS `WallpaperAgent` caches desktop images by file URL and ignores in-place file overwrites.)*
3. Iterates every screen in `NSScreen.screens` and calls:
   ```swift
   NSWorkspace.shared.setDesktopImageURL(
     fileURL,
     for: screen,
     options: [
       .imageScaling: NSImageScaling.scaleProportionallyUpOrDown.rawValue,
       .allowClipping: true
     ]
   )
   ```
4. Immediately deletes any older files in the `wallpapers/` directory except `fileURL` and `previousURL`, then schedules deletion of `previousURL` after a `2.0-second` delay on the main queue so the macOS desktop cross-fade animation completes without reading a deleted file.
5. Re-applies `lastAppliedWallpaperURL` automatically whenever `NSApplication.didChangeScreenParametersNotification`, `NSWorkspace.activeSpaceDidChangeNotification`, or `NSWorkspace.screensDidWakeNotification` fires.

### 3.3 Multi-Display Quartz Occlusion Sampling
Every `3.0 seconds` (and on workspace/space/screen/sleep/wake notifications), `DesktopWallpaperController` evaluates whether the desktop is visible:
1. **Fast Paths**:
   - If `isScreenAsleep == true`: returns `(isVisible: false, coveragePercent: 100)`.
   - If `autoPauseWhenCovered == false` or `window.isPreviewWindowVisible == true`: returns `(isVisible: true, coveragePercent: 0)`.
2. **Window List Query**:
   - Queries `CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID)`.
   - Filters to normal application windows: `kCGWindowLayer == 0`, `kCGWindowOwnerPID != myPID`, `kCGWindowAlpha >= 0.15`.
3. **Per-Display `20 × 12` Sample Grid**:
   - Converts each `NSScreen.frame` (bottom-left AppKit origin) into Quartz global coordinates (top-left origin of primary screen):
     ```text
     quartzY = primaryScreenHeight - (nsFrame.origin.y + nsFrame.height)
     ```
   - Clips all candidate window rects against `quartzScreenRect`, keeping intersections with `width > 8 && height > 8`.
   - Evaluates a uniform `20 × 12` grid (`240` cell center points) across the screen. A sample point is marked covered if it falls inside any covering window rect.
   - Computes `screenCoverage = round(coveredSamples * 100.0 / 240.0)`.
4. **Multi-Display Aggregation**:
   - Computes `minCoverage = min(screenCoverage across all connected displays)`.
   - `isVisible = (minCoverage < 88)`. As long as **at least one** connected monitor has `< 88%` window coverage, wallpaper updates continue.
   - Dispatches `onVisibilityChanged` to the UI controller whenever `isVisible` changes or `abs(coverage - lastCoveragePercent) >= 5`.
