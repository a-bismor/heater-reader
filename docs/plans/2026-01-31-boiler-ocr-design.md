# Boiler OCR Monitor — Design

Date: 2026-01-31

## Goal
Build a local, personal utility that captures images from a camera pointed at a boiler LCD, extracts four temperature values plus mode via OCR, stores the results, and displays time-series graphs with a manual correction workflow.

## Architecture & Components
- **Capture + OCR service (Python):** A scheduled loop runs every configurable interval (default 60s). It pulls a frame from the camera (RTSP preferred, ONVIF snapshot fallback), stores the raw image to disk, preprocesses it, and runs Tesseract OCR with a constrained whitelist.
- **SQLite database:** Stores original OCR readings with confidence, plus edits/verification and capture errors.
- **Web dashboard (FastAPI + simple frontend):** Shows current values, graphs over time, and a manual correction UI with image preview.
- **Config file (YAML):** Camera connection info, interval, and OCR crop coordinates.

## Data Flow & Persistence
1) Scheduler triggers capture.
2) Capture a frame.
3) Save raw image to `data/images/YYYY/MM/DD/HHMMSS.jpg`.
4) Run OCR pipeline to extract: boiler current/set temps, radiator current/set temps, and mode (`PRACA`/`PODTRZYMANIE`).
5) Insert row into SQLite with values, per-field confidence, `verified=false`, and image path.

Tables:
- **readings:** timestamp, temps, mode, confidence per field, image path, verified flag.
- **edits:** reading_id, corrected fields, editor, edited_at.
- **capture_errors:** timestamp, error string.

Queries use effective values as `COALESCE(edits.field, readings.field)` and support “verified only” filtering.

## Error Handling & Reliability
- Capture failures create a `capture_errors` row; the loop retries once and continues on the next tick.
- Low-confidence or malformed fields are stored as `NULL` and flagged in the UI for review.
- Mode is strictly whitelisted; unknown values become `UNKNOWN`.
- A `/health` endpoint reports config errors and last successful capture time.
- Run as a systemd service; logs are structured and rotated.

## UI
- Latest values panel.
- Time-series graphs for all four temperatures.
- Mode shown as step line or background band (encoded 0/1 with labels).
- Manual correction table with image preview and editable fields.

## Testing (TDD Required)
- Unit tests for OCR parsing and validation logic.
- Integration tests using fixture images through the full OCR pipeline.
- API tests for effective value queries and edits application.

## Milestones
1) Minimal capture + OCR into SQLite (CLI output for verification).
2) Read-only dashboard with graphs.
3) Manual correction workflow and verified filter.
4) Systemd service and docs polish.
