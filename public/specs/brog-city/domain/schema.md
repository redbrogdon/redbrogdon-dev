# Domain Data Models, Enumerations & Scene Geometry Schemas

This document defines the canonical data structures, enumerations, deterministic algorithms, persistent configuration schemas, and pixel-level scene coordinate tables required to implement **Brog City**.

---

## 1. Core Enumerations

### 1.1 `CityScene` (5 Intimate Diorama Archetypes)

Each scene represents a tightly zoomed-in, street-level 2.5D isometric pixel-art diorama (`1376 × 768` logical resolution, `16:9` aspect ratio) depicting **only two adjacent buildings** on a waterfront or canal corner.

| Enum Variant | `id` | `title` | Bundled Asset Path | `defaultWeather` | Reference Asset |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `twilightTramBistro` | `scene_04` | `Twilight Tram Stop & Corner Bistro` | `assets/scenes/scene_04_twilight_tram_bistro.png` | `clear` | [scene_04_twilight_tram_bistro.png](../assets/scene_04_twilight_tram_bistro.png) |
| `clocktowerFlowerShop` | `scene_07` | `Brick Clocktower Florist & Tea House` | `assets/scenes/scene_07_clocktower_flower_shop.png` | `clear` | [scene_07_clocktower_flower_shop.png](../assets/scene_07_clocktower_flower_shop.png) |
| `rainyJazzBookbinder` | `scene_08` | `Rainy Evening Jazz Cafe & Bookbinder` | `assets/scenes/scene_08_rainy_brick_arch.png` | `rain` | [scene_08_rainy_brick_arch.png](../assets/scene_08_rainy_brick_arch.png) |
| `sunlitBoathousePergola` | `scene_09` | `Sunlit Boathouse & Rooftop Pergola` | `assets/scenes/scene_09_boathouse_rooftop_garden.png` | `clear` | [scene_09_boathouse_rooftop_garden.png](../assets/scene_09_boathouse_rooftop_garden.png) |
| `winterCanalBakery` | `scene_10` | `Winter Canal Apothecary & Hearth Bakery` | `assets/scenes/scene_10_winter_canal_bakery.png` | `snow` | [scene_10_winter_canal_bakery.png](../assets/scene_10_winter_canal_bakery.png) |

#### Deterministic "Scene of the Day" Selection (`CityScene.forDate`)
When `sceneSelection` is set to `'daily_auto'` (or any string that does not match a known `CityScene.id`), the active scene is computed deterministically from the calendar date of `lastUpdateTime`:

```text
utcDay   = Date.UTC(date.year, date.month, date.day)
epoch    = Date.UTC(2026, 1, 1)
dayIndex = abs(daysBetween(utcDay, epoch))
scene    = CityScene.values[dayIndex % 5]
```

**Invariant:** Any 5 consecutive calendar days must yield all 5 distinct `CityScene` values.

---

### 1.2 `WeatherEffect`

Controls both the procedural weather overlay rendered onto the canvas and the atmospheric prompt description sent to the generative AI service.

| Variant | Override ID | Description |
| :--- | :--- | :--- |
| `clear` | `'clear'` | Diagonal warm sunbeams (on bundled scenes) and floating golden dust motes / fireflies. |
| `rain` | `'rain'` | Slate-blue atmospheric wash, two-layer diagonal pixel rain streaks, and ground/canal splash ripples. |
| `snow` | `'snow'` | Winter frost wash and multi-size drifting pixel snowflakes (including 6×6 pixel crystal crosses). |
| `mist` | `'mist'` | Silver-blue harbor mist wash and volumetric layered horizontal fog banks. |

#### Weather Resolution Priority (`activeWeather`)
1. **Live Dublin, OH Weather (`'dublin_live'`)**: If `weatherOverride == 'dublin_live'` and a cached `DublinWeatherSnapshot` is present, return `dublinWeather.mappedEffect`.
2. **Explicit Weather Override (`'clear' | 'rain' | 'snow' | 'mist'`)**: If `weatherOverride` matches a `WeatherEffect` override ID, return that effect.
3. **Scene Default Fallback (`'scene_default'` or offline `'dublin_live'`)**: Return `activeScene.defaultWeather`.

---

### 1.3 `LightingMode`

Controls the time-of-day ambient color grading and generative AI lighting prompt.

| Variant | `id` | Canvas Tint Color (ARGB Hex) | Canvas Blend Mode | Active Clock Window (`clock_sync`) |
| :--- | :--- | :--- | :--- | :--- |
| `clockSync` | `'clock_sync'` | Dynamic (see rules below) | `srcOver` | Default mode; evaluates `h = hour + minute / 60.0` |
| `original` | `'original'` | `null` (No tint applied) | N/A | N/A |
| `dawn` | `'dawn'` | `0x38FF8A65` | `softLight` | N/A |
| `daylight` | `'daylight'` | `0x28FFF9C4` | `screen` | N/A |
| `sunset` | `'sunset'` | `0x42FF6D00` | `softLight` | N/A |
| `night` | `'night'` | `0x52091326` | `srcOver` | N/A |

#### `clock_sync` Time Window Rules
Given fractional hour `h = lastUpdateTime.hour + lastUpdateTime.minute / 60.0`:

1. **Canvas Tint (`IntimateScenePainter._drawLightingTint`)**:
   - **Live AI Image Bypass:** If `isLiveGeminiImage == true` and `lightingMode == LightingMode.clockSync`, skip the canvas tint entirely (the AI model already baked the time-of-day lighting into the generated pixels).
   - `5.5 <= h < 8.0` (05:30–07:59): `0x28FF8A65` (`srcOver`, Dawn warmth)
   - `8.0 <= h < 17.0` (08:00–16:59): `null` (Pure daytime clarity, no tint)
   - `17.0 <= h < 20.0` (17:00–19:59): `0x2CFF7043` (`srcOver`, Golden hour)
   - `h >= 20.0 || h < 5.5` (20:00–05:29): `0x380D1B2A` (`srcOver`, Cozy night tone)

2. **Gemini Prompt Time Mapping (`GeminiWallpaperService._lightingFromClock`)**:
   - `5.5 <= h < 8.5`: Maps to `LightingMode.dawn`
   - `8.5 <= h < 17.0`: Maps to `LightingMode.daylight`
   - `17.0 <= h < 20.0`: Maps to `LightingMode.sunset`
   - `h >= 20.0 || h < 5.5`: Maps to `LightingMode.night`

---

## 2. Value Objects & State Snapshots

### 2.1 `DublinWeatherSnapshot`

Represents a point-in-time weather observation for Dublin, Ohio (`40.0992° N, -83.1141° W`).

| Field | Type | Default / Fallback | Description |
| :--- | :--- | :--- | :--- |
| `temperatureFahrenheit` | `double` | `62.0` | Current air temperature at 2 meters in °F. |
| `weatherCode` | `int` | `0` | WMO weather interpretation code (`0`–`99`). |
| `conditionLabel` | `String` | `'Clear Sky'` | Human-readable label mapped from `weatherCode`. |
| `mappedEffect` | `WeatherEffect` | `WeatherEffect.clear` | Corresponding `WeatherEffect` enum value. |
| `cloudCoverPercent` | `int` | `0` | Total cloud cover percentage (`0`–`100`). |
| `windSpeedMph` | `double` | `4.0` | Wind speed at 10 meters in mph. |
| `isDay` | `bool` | `true` | `true` if Open-Meteo `is_day == 1`, `false` otherwise. |
| `fetchedAt` | `DateTime` | Required | Timestamp when the snapshot was retrieved. |

#### Derived Computed Properties
- **`menuSummary`**: `"Dublin, OH: ${temperatureFahrenheit.round()}°F • $conditionLabel"` (e.g., `"Dublin, OH: 55°F • Rain"`).
- **`geminiPromptDescription`**: Constructs a natural-language atmospheric directive combining rounded temperature, `conditionLabel`, cloud cover tier (`>= 80%` overcast, `>= 35%` partly cloudy, `< 35%` mostly clear), and wind speed tier (`>= 15 mph` breezy, `< 15 mph` calm air).

#### WMO Weather Code Mapping Table (`DublinWeatherService.mapWmoCode`)

| WMO `weather_code` | `conditionLabel` | `mappedEffect` | Special Rule |
| :--- | :--- | :--- | :--- |
| `0` | `'Clear Sky'` | `clear` | — |
| `1` | `'Mostly Clear'` | `clear` | — |
| `2` | `'Partly Cloudy'` | `clear` | — |
| `3` | `'Overcast'` | `mist` if `cloudCover >= 92`, else `clear` | High-density overcast triggers harbor mist. |
| `45`, `48` | `'Fog & Mist'` | `mist` | — |
| `51`, `53`, `55`, `56`, `57` | `'Light Drizzle'` | `rain` | — |
| `61`, `63`, `65`, `66`, `67` | `'Rain'` | `rain` | — |
| `71`, `73`, `75`, `77`, `85`, `86` | `'Snowfall'` | `snow` | — |
| `80`, `81`, `82` | `'Rain Showers'` | `rain` | — |
| `95`, `96`, `99` | `'Thunderstorm'` | `rain` | — |
| Any other integer | `'Clear'` | `clear` | Default safe fallback. |

---

### 2.2 `NativeDesktopInitialState`

Returned by the native macOS host on startup via `getInitialState` to hydrate the simulation controller with persisted `UserDefaults` and live display occlusion metrics.

| Field | Type | Default Fallback | Persistent Key (`UserDefaults`) |
| :--- | :--- | :--- | :--- |
| `isDesktopVisible` | `bool` | `true` | Computed live via Quartz window list |
| `coveragePercent` | `int` | `0` | Computed live (`0`–`100`) |
| `isDesktopWallpaperMode` | `bool` | `true` | `!(window.isPreviewWindowVisible)` |
| `intervalMinutes` | `int` | `1` | `brog_city_interval_minutes` (`0`, `1`, `15`, `60`) |
| `isManuallyPaused` | `bool` | `false` | Runtime state (starts `false`) |
| `sceneSelection` | `String` | `'daily_auto'` | `brog_city_scene_selection` |
| `weatherOverride` | `String` | `'dublin_live'` | `brog_city_weather_override` |
| `lightingMode` | `String` | `'clock_sync'` | `brog_city_lighting_mode` |
| `showDiagnosticHud` | `bool` | `false` | `brog_city_show_diagnostic_hud` |
| `geminiApiKey` | `String?` | `null` | `brog_city_gemini_api_key` (or `GEMINI_API_KEY` env) |

*(Note: `brog_city_auto_pause_when_covered` is also persisted in `UserDefaults`, defaulting to `true`, and governs how `isDesktopVisible` is evaluated on the native side.)*

---

### 2.3 `GeminiGenerationResult`

Encapsulates the output of a successful live image generation call.

| Field | Type | Description |
| :--- | :--- | :--- |
| `imageBytes` | `Uint8List` | Decoded binary PNG/JPEG image payload from Gemini. |
| `promptSummary` | `String` | Short human-readable summary: `"${scene.title} • $weatherLabel • ${timeDesc.split(',').first}"`. |
| `modelUsed` | `String` | Identifier of the model that fulfilled the request (e.g., `'gemini-nano-banana-2.1'` or `'gemini-2.5-flash-image'`). |

---

## 3. Scene-Specific Coordinate Geometry (`1376 × 768` Logical Canvas)

When rendering one of the 5 bundled archetype images (`isLiveGeminiImage == false`), `IntimateScenePainter` overlays pixel-aligned animations at exact coordinates on the `1376 × 768` logical grid:

### 3.1 Scene #4: `twilightTramBistro` (`scene_04`)
- **Working Analog Tram Station Clock**:
  - Center: `(914.0, 484.0)`, Horizontal Radius `rx`: `6.0`, Vertical Radius `ry`: `8.5`
  - Hand Color: `0xFF3E2723`, Hub Color: `0xFF8D6E63`, Base Pixel Size: `1.5`
- **Red Paper Lantern Halos** (5 points, `radius: 18`, color `0xFFFF9E44` with alpha `0.14 + rng.nextDouble() * 0.10`, RNG seed `400 + updateCount * 19`):
  - `(264, 502)`, `(352, 548)`, `(442, 608)`, `(725, 608)`, `(800, 558)`
- **Streetlamp Halos** (3 points, `radius: 26`, color `0xFFFFE082` with alpha `0.16 + rng.nextDouble() * 0.08`):
  - `(176, 398)`, `(662, 650)`, `(1216, 260)`
- **Outdoor Bistro Cup Steam** (`color: 0xAAFFF8E1`, `height: 18`):
  - Table 1: Origin `(268, 628)`, seed `updateCount * 7`
  - Table 2: Origin `(365, 686)`, seed `updateCount * 13 + 3`
- **Twinkling Twilight Stars** (16 rects, `color: 0xFFFFF9C4`):
  - Indices `0..7` in upper-left sky (`x = 24 + (i * 37) % 210`), `8..15` in upper-right sky (`x = 1060 + (i * 43) % 290`), `y = 18 + (i * 29) % 140`.
  - Alpha alternates between `0.85` (`(updateCount + i) % 3 == 0`) and `0.35`; size alternates between `3×3` (`(updateCount + i) % 4 == 0`) and `2×2`.

### 3.2 Scene #7: `clocktowerFlowerShop` (`scene_07`)
- **Working Analog Clocktower Hands**:
  - Center: `(515.0, 191.0)`, Horizontal Radius `rx`: `21.0`, Vertical Radius `ry`: `31.0`
  - Hand Color: `0xFF3E1F14`, Hub Color: `0xFFB87333`, Base Pixel Size: `2.0`
- **Porcelain Teapot Steam on Dock**:
  - Origin: `(968, 692)`, Color: `0xCCFFFFFF`, Seed: `updateCount * 11`, Height: `24`
- **Drifting Golden Autumn Leaves** (RNG seed `700 + updateCount * 23`):
  - 22 two-rect pixel clusters (`4×2` and `2×2` offset by `(+2, +2)`) across `x ∈ [780, 1340)`, `y ∈ [140, 740)` cycling palette `[0xFFFFB300, 0xFFF57C00, 0xFFD84315, 0xFFFFD54F]`.
- **Canal Water Shimmer Ripples**:
  - 12 horizontal bars (`height: 2`, `width: 6..15`, color `0x88FFF3E0`) across `x ∈ [980, 1300)`, `y ∈ [320, 740)`.
- **Lantern Glows** (`color: 0x33FFD54F`):
  - Streetlamp at `(188, 560)` (`radius: 24`), Tea House porch lantern at `(1015, 398)` (`radius: 20`).

### 3.3 Scene #8: `rainyJazzBookbinder` (`scene_08`)
- **RNG Seed**: `800 + updateCount * 29`
- **Jazz Saxophone Neon Sign Glow**: Center `(575, 505)`, `radius: 28`, color `0xFFFFB74D` with alpha `0.16 + rng.nextDouble() * 0.10`.
- **Corner Streetlamp Glow**: Center `(625, 632)`, `radius: 32`, color `0x38FFE082`.
- **Viaduct Commuter Train Glows**: Headlight at `(1258, 294)` (`radius: 26`, `0x44FFE082`), carriage window at `(1312, 272)` (`radius: 22`, `0x38FFE082`).
- **Wet Cobblestone Puddle Reflections**: 18 T-shaped splash highlights (`6×2` base + `2×2` crown at `(+2, -2)`, color `0x77FFE082`) across `x ∈ [120, 1170)`, `y ∈ [620, 760)`.

### 3.4 Scene #9: `sunlitBoathousePergola` (`scene_09`)
- **RNG Seed**: `900 + updateCount * 31`
- **Terracotta Chimney Smoke**: Origin `(822, 68)`, Color `0xBBFFFFFF`, Seed `updateCount * 17`, Height `34`.
- **Turquoise Harbor Water Caustics**: 24 horizontal bars (`height: 2`, `width: 4, 8, or 12`, color `0xAAFFFFFF`) across `x ∈ [80, 1130)`, `y ∈ [580, 755)`.
- **Swimming Pixel Fish**: 5 two-rect fish silhouettes (`6×3` body + `2×2` tail at `(-2, +1)`, color `0xCC006064`) stepping horizontally via `fx = 180 + ((updateCount * 37 + i * 190) % 860)`, `fy = 645 + (i * 23) % 105`.

### 3.5 Scene #10: `winterCanalBakery` (`scene_10`)
- **RNG Seed**: `1000 + updateCount * 37`
- **Hearth Bakery Chimney Smoke**: Origin `(1242, 134)`, Color `0x99E2E8F0`, Seed `updateCount * 23`, Height `48`.
- **Flickering Stone Hearth Oven Flames**:
  - 10 vertical pixel sparks (`3×4` rects) inside `x ∈ [1266, 1286)`, `y ∈ [624, 644)` sampling colors from `[0xFFFF6D00, 0xFFFFAB00, 0xFFFFD600, 0xFFDD2C00]`.
  - Hearth glow halo at `(1276, 635)`, `radius: 26`, color `0x44FF9100`.
- **Arched Canal Bridge Lantern Halos & Water Reflection** (5 points, `radius: 22`, color `0xFFFFCC80` with alpha `0.16 + rng.nextDouble() * 0.08`):
  - Bridge lanterns: `(660, 488)`, `(758, 412)`, `(905, 610)`, `(1002, 558)`
  - Canal water reflection: `(668, 738)`
- **Apothecary Conservatory Bottle Sparkles**: 8 square glints (`3×3`, color `0xAAFFE082`) across `x ∈ [95, 385)`, `y ∈ [490, 660)`.
