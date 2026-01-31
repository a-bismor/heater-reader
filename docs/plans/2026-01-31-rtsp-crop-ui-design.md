# RTSP Crop UI Design

## Goal
Provide an interactive UI to select the crop region for a wide RTSP frame. Persist the crop rectangle in `config.yml` and apply it before OCR. The UI should show the latest snapshot image from RTSP and allow the user to draw a rectangle on it. Snapshot responses should be cached for 10 seconds to keep the UI responsive.

## Scope
- RTSP-only snapshots (no ONVIF or HTTP snapshot sources).
- In-memory 10-second cache for snapshot bytes.
- Crop persistence in `config.yml` under `capture.crop`.
- Crop applied during OCR preprocessing.
- Minimal UI overlay for rectangle selection; no external UI dependencies.

## Architecture & Data Flow
1. UI requests `/api/snapshot`.
2. Server grabs a frame from RTSP (or returns cached frame if captured within 10 seconds).
3. UI displays the JPEG and allows a rectangle to be drawn.
4. UI posts `x, y, w, h` to `/api/crop`.
5. Server writes crop values to `config.yml` under `capture.crop`.
6. OCR pipeline reads crop config and applies it to frames before OCR.

## API Endpoints
- `GET /api/snapshot`
  - Returns `image/jpeg`.
  - Uses cache if last snapshot < 10 seconds old.
  - `503` if RTSP capture fails.
- `GET /api/crop`
  - Returns current crop config or `null` if unset.
- `POST /api/crop`
  - Accepts JSON: `{ "x": int, "y": int, "w": int, "h": int }`.
  - Validates non-negative coords and `w > 0`, `h > 0`.
  - Writes to `config.yml`.

## Config Changes
Add to `config.yml`:

```yaml
capture:
  crop:
    x: 120
    y: 80
    w: 640
    h: 240
```

`CaptureConfig` gains optional `crop` field. If unset, OCR runs on full frame.

## Caching Strategy
- Store snapshot bytes and metadata in `app.state.snapshot_cache`:
  - `bytes`, `width`, `height`, `captured_at`.
- On `/api/snapshot`, if `now - captured_at < 10s`, return cached bytes.

## UI Behavior
- Add a “Crop Setup” section to dashboard.
- “Load Latest Snapshot” button triggers fetch to `/api/snapshot`.
- Draw rectangle on the image using mouse events.
- Convert drawn rectangle from display space to natural image coordinates using `naturalWidth`/`naturalHeight` scaling.
- “Save Crop” button posts to `/api/crop`.

## Error Handling
- Snapshot capture failures return 503 with JSON `{"error": "snapshot_unavailable"}`.
- Invalid crop input returns 400 with error details.

## Testing Strategy
- Unit test cache behavior by stubbing RTSP frame capture function and controlling time.
- API tests for `/api/snapshot` returning JPEG bytes and cache usage.
- API tests for `/api/crop` GET/POST validation and persistence.
- Unit test crop application logic given a fake image array.

## Out of Scope
- Multiple crop profiles.
- Persistent snapshot storage.
- Any non-RTSP capture sources.
