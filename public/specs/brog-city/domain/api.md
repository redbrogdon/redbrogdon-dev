# External APIs & Native Bridge Contracts

This document specifies all inter-process and external network contracts for **Brog City**:
1. **Native Desktop Bridge (`brog_city/desktop`)** — Bidirectional IPC between the UI/simulation runtime and the native macOS host (`DesktopWallpaperController`).
2. **Open-Meteo Weather API** — Keyless real-time meteorological telemetry for Dublin, Ohio.
3. **Google Gemini Image Generation API** — Multi-tier generative pixel-art synthesis pipeline.

---

## 1. Bidirectional Native Desktop Bridge (`brog_city/desktop`)

In the reference implementation, communication between the Flutter engine and the macOS AppKit runner occurs over a named `MethodChannel` (`"brog_city/desktop"`). Any alternative stack (e.g., Tauri IPC, Electron `ipcMain`/`ipcRenderer`, Swift/WebKit script message handlers) must implement the exact equivalent RPC calls and payloads below.

### 1.1 UI Runtime → Native Host Calls

#### `getInitialState`
Fetches persisted preferences and current display occlusion status at startup.
- **Arguments**: `none` (`null`)
- **Response (`Map<String, dynamic>`)**:
  ```json
  {
    "isDesktopVisible": true,
    "coveragePercent": 12,
    "isDesktopWallpaperMode": true,
    "intervalMinutes": 1,
    "isManuallyPaused": false,
    "sceneSelection": "daily_auto",
    "weatherOverride": "dublin_live",
    "lightingMode": "clock_sync",
    "showDiagnosticHud": false,
    "geminiApiKey": "AIzaSy..."
  }
  ```
- **Error / Headless Fallback**: If the native plugin is unavailable (e.g., in headless tests), return `null` and keep controller defaults.

#### `applyWallpaperPng`
Transfers the freshly composited `2752 × 1536` PNG byte buffer to the native host to be written to disk and applied across all connected displays.
- **Arguments (`Map<String, dynamic>`)**:
  - `"bytes"`: `Uint8List` (raw PNG file bytes)
  - `"updateCount"`: `int` (monotonic counter used to construct a unique cache-busting filename)
- **Response (`int`)**: Number of connected screens onto which the wallpaper was successfully applied (`0` on error or headless test environment).

#### `updateStatus`
Synchronizes simulation state back to the native Menu Bar so radio checkmarks (`NSMenuItem.state`) and `UserDefaults` stay consistent whenever state changes originate inside the UI runtime (e.g., clicking "Next Scene" in the preview window).
- **Arguments (`Map<String, dynamic>`)**:
  ```json
  {
    "updateCount": 4,
    "lastUpdatedTime": "14:32:05",
    "nextUpdateTime": "14:33:05",
    "isPaused": false,
    "activeSceneTitle": "Twilight Tram Stop & Corner Bistro (Daily)",
    "sceneSelection": "daily_auto",
    "weatherOverride": "dublin_live",
    "lightingMode": "clock_sync",
    "intervalMinutes": 1,
    "geminiStatus": "Dublin, OH: 55°F • Rain • Gemini AI: Live Generated (14:32:09)"
  }
  ```
- **Response**: `void` (`null`)

---

### 1.2 Native Host → UI Runtime Callbacks

The native Menu Bar (`NSStatusItem`) and display coverage monitor invoke the following methods on the UI runtime:

| Method Name | Arguments Payload | Trigger & Expected Controller Behavior |
| :--- | :--- | :--- |
| `onVisibilityChanged` | `{"visible": bool, "coveragePercent": int, "reason": String}` | Sent when display occlusion changes state (`visible` flips) or `coveragePercent` changes by `>= 5%`. If `visible == false`, cancel timer immediately. If transitioning `false -> true` while not manually paused, run catch-up check (`UNCOVER CATCH-UP`). |
| `onTriggerUpdateNow` | `null` | User clicked **Update Wallpaper Now (`⌘R`)**. Immediately increments `updateCount` (`MANUAL MENU TRIGGER`), refreshes weather/Gemini, and resets the interval timer. |
| `onCycleNextScene` | `null` | User clicked **Cycle to Next Scene (`⌘N`)**. Advances `activeScene` to `(current.index + 1) % 5`, pins `sceneSelection` to that scene's `id`, triggers update (`SCENE CYCLED`), and reschedules timer. |
| `onSetSceneSelection` | `String` (`'daily_auto'` or `'scene_04'..'scene_10'`) | User chose an item in **Scene Selection**. No-op if unchanged; otherwise updates `sceneSelection`, triggers update (`SCENE SELECTED`), and reschedules timer. |
| `onSetWeatherOverride` | `String` (`'dublin_live'`, `'scene_default'`, `'clear'`, `'rain'`, `'snow'`, `'mist'`) | User chose an item in **Weather & Atmosphere**. No-op if unchanged; otherwise updates `weatherOverride`, triggers update (`WEATHER UPDATED`), and reschedules timer. |
| `onSetLightingMode` | `String` (`'clock_sync'`, `'original'`, `'dawn'`, `'daylight'`, `'sunset'`, `'night'`) | User chose an item in **Time & Lighting Tint**. No-op if unchanged; otherwise updates `lightingMode`, triggers update (`LIGHTING UPDATED`), and reschedules timer. |
| `onSetShowDiagnosticHud` | `bool` | User toggled **Stamp Diagnostic Badge on Wallpaper**. Updates `showDiagnosticHud`, triggers an immediate local canvas re-export (`HUD TOGGLED`) **without** invoking Gemini (`regenerateWithGemini: false`), and reschedules timer. |
| `onSetPaused` | `bool` | Sets manual pause state. When unpaused, executes catch-up check (`RESUMED`). |
| `onSetUpdateIntervalMinutes` | `int` (`1`, `15`, `60`, or `0` for Never) | Normalizes values `<= 0` to `0`, otherwise clamps to `[1, 60]`. Reschedules (or cancels if `0`) the timer without forcing an immediate frame increment. |
| `onSetWindowMode` | `bool` (`isDesktopWallpaperMode`) | Sent when the user shows/hides the interactive Preview Window (`⌘W`). When `false` (Preview Window open), the bottom-right interactive control bar is rendered inside the window. |
| `onSetApiKey` | `String` | User saved a Gemini API key via the native modal alert (`⌘K`). Trims and stores the key, updates status, triggers an immediate update (`API KEY CONFIGURED`), and reschedules timer. |

---

## 2. Open-Meteo Real-Time Weather API

### 2.1 Request Specification
- **Endpoint**: `GET https://api.open-meteo.com/v1/forecast`
- **Authentication**: None (free, keyless public API)
- **Query Parameters**:
  - `latitude=40.0992` (Dublin, Ohio)
  - `longitude=-83.1141` (Dublin, Ohio)
  - `current=temperature_2m,weather_code,is_day,cloud_cover,precipitation,snowfall,wind_speed_10m`
  - `temperature_unit=fahrenheit`
  - `wind_speed_unit=mph`
- **Full Request URL**:
  ```text
  https://api.open-meteo.com/v1/forecast?latitude=40.0992&longitude=-83.1141&current=temperature_2m,weather_code,is_day,cloud_cover,precipitation,snowfall,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph
  ```
- **Timeout**: `10 seconds`

### 2.2 Caching & Fallback Policy
- **In-Memory Cache TTL (`maxAge`)**: `10 minutes`. If a cached `DublinWeatherSnapshot` exists and `abs(now - cached.fetchedAt) < 10 minutes` (and `forceRefresh == false`), return the cached snapshot without making a network request.
- **Fault Tolerance**: On HTTP status outside `200..299`, network timeout, DNS failure, or malformed JSON, catch all exceptions and return the previously cached `DublinWeatherSnapshot?` (or `null` if none has ever succeeded).

### 2.3 Expected Response Payload
```json
{
  "current": {
    "temperature_2m": 54.6,
    "weather_code": 61,
    "is_day": 1,
    "cloud_cover": 88,
    "precipitation": 0.12,
    "snowfall": 0.0,
    "wind_speed_10m": 11.4
  }
}
```

---

## 3. Google Gemini Image Generation API

### 3.1 API Key Resolution Hierarchy (`resolveApiKey`)
The service resolves the active API key by checking the following sources in strict precedence order:
1. **Runtime / Menu Bar Key**: Key set via `setApiKey()` (persisted in `UserDefaults` under `brog_city_gemini_api_key`).
2. **Compile-Time Define**: `GEMINI_API_KEY` injected at build time (e.g., `--dart-define=GEMINI_API_KEY=...`).
3. **Process Environment Variables**: `GEMINI_API_KEY` or `GOOGLE_API_KEY` from `Platform.environment`.
4. **Local Dotenv Files**: Reads `.env`, `$HOME/.brog_city.env`, and `$HOME/.env` line-by-line (ignoring `#` comments, stripping surrounding single or double quotes) looking for non-empty `GEMINI_API_KEY` or `GOOGLE_API_KEY`.

---

### 3.2 Multi-Tier Endpoint Fallback Chain

When generating a scene image, the service executes a cascading fallback strategy with a `45-second` timeout per request:

#### Tier 1: Gemini Interactions API (`gemini-nano-banana-2.1`)
- **Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/interactions`
- **Headers**:
  - `x-goog-api-key: <API_KEY>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "model": "gemini-nano-banana-2.1",
    "input": "<FULL_PROMPT>",
    "response_format": {
      "type": "image",
      "aspect_ratio": "16:9"
    }
  }
  ```

#### Tiers 2–4: Gemini `generateContent` API
If Tier 1 throws an HTTP error, times out, or returns no image bytes, iterate sequentially through the following models:
1. `gemini-2.5-flash-image`
2. `gemini-3.1-flash-image-preview`
3. `gemini-2.0-flash-preview-image-generation`

- **Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- **Headers**:
  - `x-goog-api-key: <API_KEY>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "contents": [
      {
        "parts": [
          { "text": "<FULL_PROMPT>" }
        ]
      }
    ],
    "generationConfig": {
      "responseModalities": ["IMAGE"]
    }
  }
  ```

If all 4 attempts fail, throw `GeminiApiException` concatenating all collected error messages separated by `" | "`.

---

### 3.3 Polymorphic Base64 Image Extraction (`extractBase64ImageFromJson`)

To remain resilient across API versions, response parser logic must inspect the decoded JSON map in the following order, stripping all whitespace (`\s+`) before base64-decoding:

1. **Direct Output Image**: `json['output_image']['data']` or `json['outputImage']['data']`.
2. **Nested Interaction Wrapper**: If `json['interaction']` is a Map, recursively invoke `extractBase64ImageFromJson(json['interaction'])`.
3. **Interactions `steps` Array**: Iterate `json['steps'][]`; inspect `step['content']` or `step['model_output']['content']` list; for each block, extract `block['data']` or `block['image']['data']`.
4. **Interactions `outputs` Array**: Iterate `json['outputs'][]`; extract `item['data']`.
5. **GenerateContent `candidates` Array**: Iterate `json['candidates'][]['content']['parts'][]`; inspect `part['inlineData']['data']` or `part['inline_data']['data']`.

---

### 3.4 Deterministic Prompt Synthesis (`buildPrompt`)

The prompt builder uses a deterministic PRNG seeded with:
```text
seed = now.minute + now.hour * 60 + updateCount * 131 + scene.index * 17
```
It selects:
1. **`archetype`**: One of 2 curated architectural descriptions per `CityScene` (describing the exact left and right buildings, bridge/canal, and textures).
2. **`microLife`**: One of 6 ambient micro-activities (e.g., pixel barista serving steaming cups while a calico cat naps upstairs; wooden rowboat with bow lantern; neighbors chatting under streetlamp; reader by upstairs desk lamp; delivery bicycle with wicker basket; ducks swimming past dock posts).
3. **`timeDesc`**: Lighting description derived from `lightingMode` (or `_lightingFromClock(now)` when in `clock_sync`).
4. **`weatherDesc`**: `dublinWeather.geminiPromptDescription` if live Dublin weather is present, otherwise a rich description of `weather`.

#### Canonical Prompt Template
```text
Masterpiece 32-bit HD isometric 2.5D pixel art illustration in a 16:9 widescreen format. CAMERA & SCALE: Tightly zoomed-in, intimate street-level isometric diorama showing ONLY TWO adjacent buildings on a small waterfront or canal corner. Do NOT show a wide city skyline or distant buildings; the two featured buildings, their alleyway/bridge, and the adjacent water should fill 85% of the frame. ARCHITECTURAL SUBJECT: <archetype> LIVE MOMENT IN TIME: <microLife> TIME OF DAY & LIGHTING: <timeDesc> WEATHER & ATMOSPHERE: <weatherDesc> ART STYLE: Crisp, hand-crafted pixel art with distinct pixel clusters, warm interior cutaway lighting visible through windows, rich brick, stone, timber, and terracotta textures, pixel water reflections, inspired by Octopath Traveler and Eastward. No UI, no overlays, no watermarks.
```
