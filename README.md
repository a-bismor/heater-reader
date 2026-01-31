# Boiler OCR Monitor

Local service that captures boiler LCD images, extracts temperature readings via OCR, stores them in SQLite, and serves a simple web dashboard for graphs and manual corrections.

## Setup
1. Create a virtualenv and install requirements.
2. Create `config.yml` with camera settings.
3. Run the API: `uvicorn heater_reader.app:create_app --factory --reload`.

## Config

```yaml
capture:
  interval_seconds: 60
  image_root: data/images
  rtsp_url: rtsp://user:pass@camera/stream
  onvif_snapshot_url: http://camera/snapshot.jpg
```
