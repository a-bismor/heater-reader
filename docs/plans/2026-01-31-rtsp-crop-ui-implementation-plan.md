# RTSP Crop UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add RTSP snapshot capture with 10s caching, interactive crop selection UI, and persisted crop configuration applied before OCR.

**Architecture:** The FastAPI app serves a snapshot endpoint that grabs a single RTSP frame via OpenCV and caches it in memory for 10 seconds. A crop endpoint persists `x,y,w,h` in `config.yml`. The frontend displays the snapshot and lets the user draw a rectangle, converting display coords to natural image coords before saving. OCR applies the crop if configured.

**Tech Stack:** Python 3.10+, FastAPI, OpenCV, PyYAML, Chart.js (existing), vanilla JS.

---

### Task 1: Extend config schema with crop settings

**Files:**
- Modify: `src/heater_reader/config.py`
- Create: `tests/test_config_crop.py`

**Step 1: Write the failing test**

```python
# tests/test_config_crop.py
from pathlib import Path
from heater_reader.config import load_config


def test_load_config_parses_crop_settings(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
        capture:
          crop:
            x: 10
            y: 20
            w: 300
            h: 200
        """
    )

    cfg = load_config(config_path)

    assert cfg.capture.crop == {"x": 10, "y": 20, "w": 300, "h": 200}
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_config_crop.py::test_load_config_parses_crop_settings -v`
Expected: FAIL (attribute missing)

**Step 3: Write minimal implementation**

```python
# src/heater_reader/config.py (additions)
from typing import Any

@dataclass
class CaptureConfig:
    interval_seconds: int = 60
    image_root: Path = Path("data/images")
    rtsp_url: str | None = None
    onvif_snapshot_url: str | None = None
    crop: dict[str, int] | None = None


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text()) if path.exists() else {}
    capture_raw = (raw or {}).get("capture", {})
    crop_raw = capture_raw.get("crop")
    crop = None
    if isinstance(crop_raw, dict):
        crop = {
            "x": int(crop_raw.get("x", 0)),
            "y": int(crop_raw.get("y", 0)),
            "w": int(crop_raw.get("w", 0)),
            "h": int(crop_raw.get("h", 0)),
        }

    capture = CaptureConfig(
        interval_seconds=int(capture_raw.get("interval_seconds", 60)),
        image_root=Path(capture_raw.get("image_root", "data/images")),
        rtsp_url=capture_raw.get("rtsp_url"),
        onvif_snapshot_url=capture_raw.get("onvif_snapshot_url"),
        crop=crop,
    )
    return AppConfig(capture=capture)
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_config_crop.py::test_load_config_parses_crop_settings -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/config.py tests/test_config_crop.py
git commit -m "feat: add crop config support"
```

---

### Task 2: Add RTSP snapshot capture with 10s cache

**Files:**
- Modify: `src/heater_reader/capture.py`
- Create: `tests/test_snapshot_cache.py`

**Step 1: Write the failing test**

```python
# tests/test_snapshot_cache.py
from datetime import datetime, timedelta, timezone
from heater_reader.capture import SnapshotCache


def test_snapshot_cache_returns_cached_within_ttl():
    now = datetime(2026, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
    cache = SnapshotCache(ttl_seconds=10)

    cache.set(b"img", width=100, height=50, captured_at=now)

    assert cache.get(now + timedelta(seconds=9)) is not None
    assert cache.get(now + timedelta(seconds=11)) is None
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_snapshot_cache.py::test_snapshot_cache_returns_cached_within_ttl -v`
Expected: FAIL (SnapshotCache missing)

**Step 3: Write minimal implementation**

```python
# src/heater_reader/capture.py (additions)
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Snapshot:
    bytes: bytes
    width: int
    height: int
    captured_at: datetime


class SnapshotCache:
    def __init__(self, ttl_seconds: int = 10) -> None:
        self._ttl = ttl_seconds
        self._snapshot: Snapshot | None = None

    def get(self, now: datetime) -> Snapshot | None:
        if self._snapshot is None:
            return None
        age = (now - self._snapshot.captured_at).total_seconds()
        if age > self._ttl:
            return None
        return self._snapshot

    def set(self, data: bytes, width: int, height: int, captured_at: datetime | None = None) -> None:
        if captured_at is None:
            captured_at = datetime.now(timezone.utc)
        self._snapshot = Snapshot(data, width, height, captured_at)
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_snapshot_cache.py::test_snapshot_cache_returns_cached_within_ttl -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/capture.py tests/test_snapshot_cache.py
git commit -m "feat: add snapshot cache"
```

---

### Task 3: Add RTSP single-frame capture helper

**Files:**
- Modify: `src/heater_reader/capture.py`
- Create: `tests/test_rtsp_capture.py`

**Step 1: Write the failing test**

```python
# tests/test_rtsp_capture.py
from heater_reader.capture import encode_frame_to_jpeg


def test_encode_frame_to_jpeg_returns_bytes():
    import numpy as np

    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    data = encode_frame_to_jpeg(frame)

    assert isinstance(data, (bytes, bytearray))
    assert len(data) > 0
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_rtsp_capture.py::test_encode_frame_to_jpeg_returns_bytes -v`
Expected: FAIL (function missing)

**Step 3: Write minimal implementation**

```python
# src/heater_reader/capture.py (additions)
import cv2
import numpy as np


def encode_frame_to_jpeg(frame: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise ValueError("Failed to encode frame")
    return buf.tobytes()
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_rtsp_capture.py::test_encode_frame_to_jpeg_returns_bytes -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/capture.py tests/test_rtsp_capture.py
git commit -m "feat: add RTSP frame encoding"
```

---

### Task 4: Add snapshot API endpoints (GET /api/snapshot, GET/POST /api/crop)

**Files:**
- Modify: `src/heater_reader/api.py`
- Modify: `src/heater_reader/app.py`
- Create: `tests/test_api_snapshot.py`
- Create: `tests/test_api_crop.py`

**Step 1: Write the failing test**

```python
# tests/test_api_snapshot.py
from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_snapshot_endpoint_returns_jpeg(monkeypatch):
    def fake_snapshot(rtsp_url):
        return b"jpeg", 10, 10

    app = create_app("data/readings.db", rtsp_url="rtsp://example")
    app.state.get_snapshot = fake_snapshot
    client = TestClient(app)

    response = client.get("/api/snapshot")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/jpeg")
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_api_snapshot.py::test_snapshot_endpoint_returns_jpeg -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/app.py (additions)
from heater_reader.capture import SnapshotCache, fetch_rtsp_snapshot


def create_app(db_path: str, rtsp_url: str | None = None) -> FastAPI:
    app = FastAPI()
    app.state.db_path = db_path
    app.state.rtsp_url = rtsp_url
    app.state.snapshot_cache = SnapshotCache(ttl_seconds=10)

    def get_snapshot(url: str):
        return fetch_rtsp_snapshot(url)

    app.state.get_snapshot = get_snapshot
    app.include_router(router)
    return app
```

```python
# src/heater_reader/api.py (additions)
from fastapi import Response, HTTPException
from datetime import datetime, timezone


@router.get("/api/snapshot")
def snapshot(request: Request):
    rtsp_url = request.app.state.rtsp_url
    if not rtsp_url:
        raise HTTPException(status_code=400, detail="rtsp_url_missing")

    cache = request.app.state.snapshot_cache
    now = datetime.now(timezone.utc)
    cached = cache.get(now)
    if cached:
        return Response(content=cached.bytes, media_type="image/jpeg")

    try:
        data, width, height = request.app.state.get_snapshot(rtsp_url)
    except Exception:
        raise HTTPException(status_code=503, detail="snapshot_unavailable")

    cache.set(data, width=width, height=height, captured_at=now)
    return Response(content=data, media_type="image/jpeg")
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_api_snapshot.py::test_snapshot_endpoint_returns_jpeg -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/app.py src/heater_reader/api.py tests/test_api_snapshot.py
git commit -m "feat: add snapshot endpoint"
```

---

### Task 5: Add crop API and config persistence

**Files:**
- Modify: `src/heater_reader/api.py`
- Modify: `src/heater_reader/config.py`
- Create: `tests/test_api_crop.py`

**Step 1: Write the failing test**

```python
# tests/test_api_crop.py
from fastapi.testclient import TestClient
from pathlib import Path
from heater_reader.app import create_app


def test_crop_endpoint_persists_config(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("capture:\n  interval_seconds: 60\n")

    app = create_app("data/readings.db")
    app.state.config_path = config_path
    client = TestClient(app)

    response = client.post("/api/crop", json={"x": 1, "y": 2, "w": 3, "h": 4})
    assert response.status_code == 200

    text = config_path.read_text()
    assert "crop" in text
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_api_crop.py::test_crop_endpoint_persists_config -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/app.py (additions)
from pathlib import Path


def create_app(db_path: str, rtsp_url: str | None = None, config_path: Path | None = None) -> FastAPI:
    app = FastAPI()
    app.state.db_path = db_path
    app.state.rtsp_url = rtsp_url
    app.state.config_path = config_path or Path("config.yml")
    app.state.snapshot_cache = SnapshotCache(ttl_seconds=10)
    ...
```

```python
# src/heater_reader/api.py (additions)
from pydantic import BaseModel
import yaml


class CropPayload(BaseModel):
    x: int
    y: int
    w: int
    h: int


@router.get("/api/crop")
def get_crop(request: Request):
    cfg = load_config(request.app.state.config_path)
    return cfg.capture.crop


@router.post("/api/crop")
def set_crop(payload: CropPayload, request: Request):
    if payload.w <= 0 or payload.h <= 0 or payload.x < 0 or payload.y < 0:
        raise HTTPException(status_code=400, detail="invalid_crop")

    config_path = request.app.state.config_path
    raw = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
    raw = raw or {}
    raw.setdefault("capture", {})["crop"] = {
        "x": payload.x,
        "y": payload.y,
        "w": payload.w,
        "h": payload.h,
    }
    config_path.write_text(yaml.safe_dump(raw, sort_keys=False))
    return raw["capture"]["crop"]
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_api_crop.py::test_crop_endpoint_persists_config -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/api.py src/heater_reader/app.py src/heater_reader/config.py tests/test_api_crop.py
git commit -m "feat: add crop config endpoints"
```

---

### Task 6: Apply crop before OCR

**Files:**
- Modify: `src/heater_reader/ocr_pipeline.py`
- Modify: `src/heater_reader/capture.py`
- Create: `tests/test_crop_apply.py`

**Step 1: Write the failing test**

```python
# tests/test_crop_apply.py
import numpy as np
from heater_reader.ocr_pipeline import apply_crop


def test_apply_crop_slices_image():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    crop = {"x": 10, "y": 5, "w": 50, "h": 20}

    sliced = apply_crop(img, crop)

    assert sliced.shape[0] == 20
    assert sliced.shape[1] == 50
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_crop_apply.py::test_apply_crop_slices_image -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/ocr_pipeline.py (additions)
import numpy as np


def apply_crop(image: np.ndarray, crop: dict[str, int] | None) -> np.ndarray:
    if not crop:
        return image
    x = crop.get("x", 0)
    y = crop.get("y", 0)
    w = crop.get("w", 0)
    h = crop.get("h", 0)
    return image[y : y + h, x : x + w]
```

```python
# src/heater_reader/ocr_pipeline.py (modify extract_text_from_image)
from heater_reader.config import load_config


def extract_text_from_image(path: Path, config_path: Path | None = None) -> str:
    image = cv2.imread(str(path))
    if config_path:
        cfg = load_config(config_path)
        image = apply_crop(image, cfg.capture.crop)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_crop_apply.py::test_apply_crop_slices_image -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/ocr_pipeline.py tests/test_crop_apply.py

git commit -m "feat: apply crop before OCR"
```

---

### Task 7: Add crop UI overlay

**Files:**
- Modify: `src/heater_reader/static/index.html`
- Create: `tests/test_ui_crop.py`

**Step 1: Write the failing test**

```python
# tests/test_ui_crop.py
from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_crop_ui_includes_button():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Load Latest Snapshot" in response.text
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_ui_crop.py::test_crop_ui_includes_button -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```html
<!-- src/heater_reader/static/index.html (additions) -->
<section id="crop-setup">
  <h2>Crop Setup</h2>
  <button id="load-snapshot">Load Latest Snapshot</button>
  <button id="save-crop" disabled>Save Crop</button>
  <div style="position: relative; display: inline-block;">
    <img id="snapshot" alt="Latest snapshot" />
    <div id="crop-rect" style="position: absolute; border: 2px solid red; display: none;"></div>
  </div>
</section>
<script>
  // basic drag-to-draw rectangle on #snapshot
</script>
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_ui_crop.py::test_crop_ui_includes_button -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/static/index.html tests/test_ui_crop.py
git commit -m "feat: add crop setup UI"
```

---

### Task 8: Add snapshot UI wiring and crop POST

**Files:**
- Modify: `src/heater_reader/static/index.html`

**Step 1: Write the failing test**

```python
# tests/test_ui_crop.py (add)

def test_crop_ui_has_save_handler():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert "save-crop" in response.text
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_ui_crop.py::test_crop_ui_has_save_handler -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```html
<!-- src/heater_reader/static/index.html (additions) -->
<script>
  const snapshot = document.getElementById("snapshot");
  const cropRect = document.getElementById("crop-rect");
  const loadBtn = document.getElementById("load-snapshot");
  const saveBtn = document.getElementById("save-crop");
  let rect = null;

  loadBtn.addEventListener("click", async () => {
    const resp = await fetch("/api/snapshot");
    const blob = await resp.blob();
    snapshot.src = URL.createObjectURL(blob);
  });

  // pointer handlers to set rect

  saveBtn.addEventListener("click", async () => {
    if (!rect) return;
    const scaleX = snapshot.naturalWidth / snapshot.clientWidth;
    const scaleY = snapshot.naturalHeight / snapshot.clientHeight;
    const payload = {
      x: Math.round(rect.x * scaleX),
      y: Math.round(rect.y * scaleY),
      w: Math.round(rect.w * scaleX),
      h: Math.round(rect.h * scaleY),
    };
    await fetch("/api/crop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  });
</script>
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/pytest tests/test_ui_crop.py::test_crop_ui_has_save_handler -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/static/index.html tests/test_ui_crop.py
git commit -m "feat: wire crop UI"
```

---

## Plan complete and saved to `docs/plans/2026-01-31-rtsp-crop-ui-implementation-plan.md`.

Two execution options:

1. Subagent-Driven (this session) — I dispatch fresh subagent per task, review between tasks
2. Parallel Session (separate) — open new session with executing-plans, batch execution with checkpoints

Which approach?
