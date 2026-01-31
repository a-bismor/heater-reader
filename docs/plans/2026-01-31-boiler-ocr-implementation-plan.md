# Boiler OCR Monitor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local service that captures boiler LCD images, extracts four temperature values and mode via OCR, stores them in SQLite, and serves a web dashboard with graphs and manual correction.

**Architecture:** A Python service provides two concerns: capture/OCR pipeline and a FastAPI web app. Data is stored in SQLite; raw images are saved on disk and linked from readings. The frontend is a simple HTML page with Chart.js, served by FastAPI.

**Tech Stack:** Python 3.10+, FastAPI, Uvicorn, SQLite, OpenCV, pytesseract, Chart.js.

---

### Task 1: Establish Python project structure and dependencies

**Files:**
- Create: `requirements.txt`
- Create: `src/heater_reader/__init__.py`
- Create: `src/heater_reader/config.py`
- Create: `src/heater_reader/paths.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
from heater_reader.config import AppConfig, load_config


def test_load_config_uses_defaults_when_missing_fields(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text("capture:\n  interval_seconds: 60\n")

    cfg = load_config(config_path)

    assert cfg.capture.interval_seconds == 60
    assert cfg.capture.image_root.name == "images"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py::test_load_config_uses_defaults_when_missing_fields -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

```python
# src/heater_reader/config.py
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class CaptureConfig:
    interval_seconds: int = 60
    image_root: Path = Path("data/images")
    rtsp_url: str | None = None
    onvif_snapshot_url: str | None = None


@dataclass
class AppConfig:
    capture: CaptureConfig = CaptureConfig()


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text()) if path.exists() else {}
    capture_raw = (raw or {}).get("capture", {})

    capture = CaptureConfig(
        interval_seconds=int(capture_raw.get("interval_seconds", 60)),
        image_root=Path(capture_raw.get("image_root", "data/images")),
        rtsp_url=capture_raw.get("rtsp_url"),
        onvif_snapshot_url=capture_raw.get("onvif_snapshot_url"),
    )
    return AppConfig(capture=capture)
```

```python
# src/heater_reader/paths.py
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py::test_load_config_uses_defaults_when_missing_fields -v`
Expected: PASS

**Step 5: Commit**

```bash
git add requirements.txt src/heater_reader/__init__.py src/heater_reader/config.py src/heater_reader/paths.py tests/test_config.py
git commit -m "feat: add config loader and defaults"
```

---

### Task 2: Add capture scheduling and image storage

**Files:**
- Create: `src/heater_reader/capture.py`
- Create: `tests/test_capture.py`

**Step 1: Write the failing test**

```python
# tests/test_capture.py
from datetime import datetime, timezone
from pathlib import Path
from heater_reader.capture import image_path_for


def test_image_path_for_creates_timestamped_path():
    root = Path("data/images")
    ts = datetime(2026, 1, 31, 10, 5, 6, tzinfo=timezone.utc)

    path = image_path_for(root, ts)

    assert str(path).endswith("/2026/01/31/100506.jpg")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_capture.py::test_image_path_for_creates_timestamped_path -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

```python
# src/heater_reader/capture.py
from datetime import datetime
from pathlib import Path


def image_path_for(root: Path, ts: datetime) -> Path:
    return root / ts.strftime("%Y/%m/%d/%H%M%S.jpg")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_capture.py::test_image_path_for_creates_timestamped_path -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/capture.py tests/test_capture.py
git commit -m "feat: add image path helper"
```

---

### Task 3: Implement OCR parsing for temps and mode

**Files:**
- Create: `src/heater_reader/ocr.py`
- Create: `tests/test_ocr.py`

**Step 1: Write the failing test**

```python
# tests/test_ocr.py
from heater_reader.ocr import parse_reading


def test_parse_reading_extracts_temps_and_mode():
    text = "C.O. 45/55 C.W.U. 42/50 PRACA"
    reading = parse_reading(text)

    assert reading.boiler_current == 45
    assert reading.boiler_set == 55
    assert reading.radiator_current == 42
    assert reading.radiator_set == 50
    assert reading.mode == "PRACA"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ocr.py::test_parse_reading_extracts_temps_and_mode -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/ocr.py
from dataclasses import dataclass
import re


@dataclass
class ReadingText:
    boiler_current: int | None
    boiler_set: int | None
    radiator_current: int | None
    radiator_set: int | None
    mode: str


_TEMP_PAIR = re.compile(r"(\d{1,3})\s*/\s*(\d{1,3})")


def parse_reading(text: str) -> ReadingText:
    pairs = _TEMP_PAIR.findall(text)
    boiler_current = boiler_set = radiator_current = radiator_set = None
    if len(pairs) >= 2:
        boiler_current, boiler_set = map(int, pairs[0])
        radiator_current, radiator_set = map(int, pairs[1])

    mode = "UNKNOWN"
    if "PRACA" in text:
        mode = "PRACA"
    elif "PODTRZYMANIE" in text:
        mode = "PODTRZYMANIE"

    return ReadingText(
        boiler_current=boiler_current,
        boiler_set=boiler_set,
        radiator_current=radiator_current,
        radiator_set=radiator_set,
        mode=mode,
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ocr.py::test_parse_reading_extracts_temps_and_mode -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/ocr.py tests/test_ocr.py
git commit -m "feat: add OCR text parser"
```

---

### Task 4: Add SQLite schema and repository layer

**Files:**
- Create: `src/heater_reader/db.py`
- Create: `tests/test_db.py`

**Step 1: Write the failing test**

```python
# tests/test_db.py
from pathlib import Path
from heater_reader.db import Database
from heater_reader.ocr import ReadingText


def test_insert_and_fetch_reading(tmp_path):
    db_path = tmp_path / "readings.db"
    db = Database(db_path)
    db.init_schema()

    reading_id = db.insert_reading(
        ReadingText(45, 55, 42, 50, "PRACA"),
        image_path="data/images/2026/01/31/100506.jpg",
    )

    row = db.get_reading(reading_id)
    assert row["boiler_current"] == 45
    assert row["mode"] == "PRACA"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_db.py::test_insert_and_fetch_reading -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/db.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from heater_reader.ocr import ReadingText


@dataclass
class Database:
    path: Path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY,
                    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
                    boiler_current INTEGER,
                    boiler_set INTEGER,
                    radiator_current INTEGER,
                    radiator_set INTEGER,
                    mode TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    verified INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS edits (
                    id INTEGER PRIMARY KEY,
                    reading_id INTEGER NOT NULL,
                    boiler_current INTEGER,
                    boiler_set INTEGER,
                    radiator_current INTEGER,
                    radiator_set INTEGER,
                    mode TEXT,
                    edited_by TEXT NOT NULL,
                    edited_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (reading_id) REFERENCES readings(id)
                );

                CREATE TABLE IF NOT EXISTS capture_errors (
                    id INTEGER PRIMARY KEY,
                    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
                    error TEXT NOT NULL
                );
                """
            )

    def insert_reading(self, reading: ReadingText, image_path: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO readings (
                    boiler_current, boiler_set, radiator_current, radiator_set, mode, image_path
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    reading.boiler_current,
                    reading.boiler_set,
                    reading.radiator_current,
                    reading.radiator_set,
                    reading.mode,
                    image_path,
                ),
            )
            return int(cur.lastrowid)

    def get_reading(self, reading_id: int) -> sqlite3.Row:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM readings WHERE id = ?", (reading_id,))
            return cur.fetchone()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_db.py::test_insert_and_fetch_reading -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/db.py tests/test_db.py
git commit -m "feat: add sqlite schema and repository"
```

---

### Task 5: OCR pipeline stub (image to text) with fixtures

**Files:**
- Create: `src/heater_reader/ocr_pipeline.py`
- Create: `tests/test_ocr_pipeline.py`
- Create: `tests/fixtures/README.md`

**Step 1: Write the failing test**

```python
# tests/test_ocr_pipeline.py
from pathlib import Path
from heater_reader.ocr_pipeline import extract_text_from_image


def test_extract_text_from_image_returns_string(tmp_path):
    image_path = Path("tests/fixtures/sample_lcd.jpg")
    if not image_path.exists():
        return  # placeholder until fixture added

    text = extract_text_from_image(image_path)

    assert isinstance(text, str)
    assert text.strip() != ""
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ocr_pipeline.py::test_extract_text_from_image_returns_string -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/ocr_pipeline.py
from pathlib import Path
import pytesseract
import cv2


def extract_text_from_image(path: Path) -> str:
    image = cv2.imread(str(path))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)
```

```markdown
# tests/fixtures/README.md
Place LCD sample images in this folder (e.g., sample_lcd.jpg) to enable OCR integration tests.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ocr_pipeline.py::test_extract_text_from_image_returns_string -v`
Expected: PASS if fixture is present

**Step 5: Commit**

```bash
git add src/heater_reader/ocr_pipeline.py tests/test_ocr_pipeline.py tests/fixtures/README.md
git commit -m "feat: add OCR pipeline stub"
```

---

### Task 6: Capture + OCR integration (no scheduling yet)

**Files:**
- Modify: `src/heater_reader/capture.py`
- Create: `tests/test_capture_integration.py`

**Step 1: Write the failing test**

```python
# tests/test_capture_integration.py
from pathlib import Path
from heater_reader.capture import capture_and_ocr
from heater_reader.ocr import ReadingText


def test_capture_and_ocr_handles_missing_frame(tmp_path):
    image_path = tmp_path / "missing.jpg"

    result = capture_and_ocr(image_path)

    assert result is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_capture_integration.py::test_capture_and_ocr_handles_missing_frame -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/capture.py
from pathlib import Path
from heater_reader.ocr_pipeline import extract_text_from_image
from heater_reader.ocr import parse_reading, ReadingText


def capture_and_ocr(image_path: Path) -> ReadingText | None:
    if not image_path.exists():
        return None

    text = extract_text_from_image(image_path)
    return parse_reading(text)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_capture_integration.py::test_capture_and_ocr_handles_missing_frame -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/capture.py tests/test_capture_integration.py
git commit -m "feat: add capture+ocr integration stub"
```

---

### Task 7: FastAPI app skeleton and readings API

**Files:**
- Create: `src/heater_reader/api.py`
- Create: `src/heater_reader/app.py`
- Create: `tests/test_api.py`

**Step 1: Write the failing test**

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_health_endpoint_ok():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_api.py::test_health_endpoint_ok -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/app.py
from fastapi import FastAPI
from heater_reader.api import router


def create_app(db_path: str) -> FastAPI:
    app = FastAPI()
    app.state.db_path = db_path
    app.include_router(router)
    return app
```

```python
# src/heater_reader/api.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_api.py::test_health_endpoint_ok -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/app.py src/heater_reader/api.py tests/test_api.py
git commit -m "feat: add FastAPI skeleton"
```

---

### Task 8: Readings API with effective values

**Files:**
- Modify: `src/heater_reader/db.py`
- Modify: `src/heater_reader/api.py`
- Modify: `tests/test_db.py`
- Create: `tests/test_api_readings.py`

**Step 1: Write the failing test**

```python
# tests/test_db.py
from heater_reader.db import Database
from heater_reader.ocr import ReadingText


def test_effective_readings_use_edits(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    db.init_schema()

    reading_id = db.insert_reading(
        ReadingText(45, 55, 42, 50, "PRACA"),
        image_path="path.jpg",
    )
    db.insert_edit(reading_id, boiler_current=47, edited_by="adam")

    row = db.get_effective_reading(reading_id)
    assert row["boiler_current"] == 47
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_db.py::test_effective_readings_use_edits -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/db.py (additions)
    def insert_edit(
        self,
        reading_id: int,
        boiler_current: int | None = None,
        boiler_set: int | None = None,
        radiator_current: int | None = None,
        radiator_set: int | None = None,
        mode: str | None = None,
        edited_by: str = "adam",
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO edits (reading_id, boiler_current, boiler_set, radiator_current, radiator_set, mode, edited_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reading_id,
                    boiler_current,
                    boiler_set,
                    radiator_current,
                    radiator_set,
                    mode,
                    edited_by,
                ),
            )
            return int(cur.lastrowid)

    def get_effective_reading(self, reading_id: int):
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT
                    r.id,
                    COALESCE(e.boiler_current, r.boiler_current) AS boiler_current,
                    COALESCE(e.boiler_set, r.boiler_set) AS boiler_set,
                    COALESCE(e.radiator_current, r.radiator_current) AS radiator_current,
                    COALESCE(e.radiator_set, r.radiator_set) AS radiator_set,
                    COALESCE(e.mode, r.mode) AS mode,
                    r.image_path
                FROM readings r
                LEFT JOIN edits e ON e.reading_id = r.id
                WHERE r.id = ?
                ORDER BY e.edited_at DESC
                LIMIT 1
                """,
                (reading_id,),
            )
            return cur.fetchone()
```

```python
# tests/test_api_readings.py
from fastapi.testclient import TestClient
from heater_reader.app import create_app
from heater_reader.db import Database
from heater_reader.ocr import ReadingText


def test_readings_endpoint_returns_effective_values(tmp_path):
    db_path = tmp_path / "db.sqlite"
    db = Database(db_path)
    db.init_schema()
    reading_id = db.insert_reading(ReadingText(45, 55, 42, 50, "PRACA"), image_path="path.jpg")
    db.insert_edit(reading_id, boiler_current=47, edited_by="adam")

    app = create_app(str(db_path))
    client = TestClient(app)

    response = client.get("/api/readings")
    assert response.status_code == 200
    assert response.json()[0]["boiler_current"] == 47
```

```python
# src/heater_reader/api.py (additions)
from heater_reader.db import Database
from fastapi import Request


@router.get("/api/readings")
def readings(request: Request):
    db = Database(request.app.state.db_path)
    rows = db.list_effective_readings()
    return [dict(row) for row in rows]
```

```python
# src/heater_reader/db.py (additions)
    def list_effective_readings(self):
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT
                    r.id,
                    COALESCE(e.boiler_current, r.boiler_current) AS boiler_current,
                    COALESCE(e.boiler_set, r.boiler_set) AS boiler_set,
                    COALESCE(e.radiator_current, r.radiator_current) AS radiator_current,
                    COALESCE(e.radiator_set, r.radiator_set) AS radiator_set,
                    COALESCE(e.mode, r.mode) AS mode,
                    r.captured_at
                FROM readings r
                LEFT JOIN edits e ON e.reading_id = r.id
                ORDER BY r.captured_at ASC
                """
            )
            return cur.fetchall()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_db.py::test_effective_readings_use_edits -v`
Expected: PASS

Run: `pytest tests/test_api_readings.py::test_readings_endpoint_returns_effective_values -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/db.py src/heater_reader/api.py tests/test_db.py tests/test_api_readings.py
git commit -m "feat: add effective readings and API"
```

---

### Task 9: Simple web UI with charts

**Files:**
- Create: `src/heater_reader/static/index.html`
- Modify: `src/heater_reader/api.py`
- Create: `tests/test_ui.py`

**Step 1: Write the failing test**

```python
# tests/test_ui.py
from fastapi.testclient import TestClient
from heater_reader.app import create_app


def test_index_html_served():
    app = create_app("data/readings.db")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Boiler" in response.text
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui.py::test_index_html_served -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/api.py (additions)
from fastapi.responses import HTMLResponse
from pathlib import Path


@router.get("/")
def index():
    html = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(html.read_text())
```

```html
<!-- src/heater_reader/static/index.html -->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Boiler Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body>
    <h1>Boiler Monitor</h1>
    <canvas id="temps"></canvas>
    <script>
      async function loadData() {
        const response = await fetch("/api/readings");
        const data = await response.json();
        const labels = data.map((r) => r.captured_at);
        const boilerCurrent = data.map((r) => r.boiler_current);
        const boilerSet = data.map((r) => r.boiler_set);
        const radiatorCurrent = data.map((r) => r.radiator_current);
        const radiatorSet = data.map((r) => r.radiator_set);

        new Chart(document.getElementById("temps"), {
          type: "line",
          data: {
            labels,
            datasets: [
              { label: "Boiler Current", data: boilerCurrent },
              { label: "Boiler Set", data: boilerSet },
              { label: "Radiator Current", data: radiatorCurrent },
              { label: "Radiator Set", data: radiatorSet },
            ],
          },
        });
      }
      loadData();
    </script>
  </body>
</html>
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui.py::test_index_html_served -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/static/index.html src/heater_reader/api.py tests/test_ui.py
git commit -m "feat: add dashboard HTML"
```

---

### Task 10: Manual correction API and UI table

**Files:**
- Modify: `src/heater_reader/api.py`
- Modify: `src/heater_reader/static/index.html`
- Modify: `src/heater_reader/db.py`
- Create: `tests/test_edits_api.py`

**Step 1: Write the failing test**

```python
# tests/test_edits_api.py
from fastapi.testclient import TestClient
from heater_reader.app import create_app
from heater_reader.db import Database
from heater_reader.ocr import ReadingText


def test_post_edit_updates_effective_values(tmp_path):
    db_path = tmp_path / "db.sqlite"
    db = Database(db_path)
    db.init_schema()
    reading_id = db.insert_reading(ReadingText(45, 55, 42, 50, "PRACA"), image_path="path.jpg")

    app = create_app(str(db_path))
    client = TestClient(app)

    response = client.post(
        "/api/readings/1/edit",
        json={"boiler_current": 48, "edited_by": "adam"},
    )

    assert response.status_code == 200
    assert response.json()["boiler_current"] == 48
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_edits_api.py::test_post_edit_updates_effective_values -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/api.py (additions)
from pydantic import BaseModel


class EditPayload(BaseModel):
    boiler_current: int | None = None
    boiler_set: int | None = None
    radiator_current: int | None = None
    radiator_set: int | None = None
    mode: str | None = None
    edited_by: str = "adam"


@router.post("/api/readings/{reading_id}/edit")
def edit_reading(reading_id: int, payload: EditPayload, request: Request):
    db = Database(request.app.state.db_path)
    db.insert_edit(reading_id, **payload.dict())
    row = db.get_effective_reading(reading_id)
    return dict(row)
```

```html
<!-- src/heater_reader/static/index.html (add table + edit form) -->
<table id="readings"></table>
<script>
  async function loadTable() {
    const response = await fetch("/api/readings");
    const data = await response.json();
    const table = document.getElementById("readings");
    table.innerHTML = "<tr><th>Time</th><th>Boiler Current</th><th>Boiler Set</th><th>Radiator Current</th><th>Radiator Set</th><th>Mode</th></tr>";
    for (const row of data) {
      table.innerHTML += `<tr>
        <td>${row.captured_at}</td>
        <td contenteditable data-field="boiler_current" data-id="${row.id}">${row.boiler_current ?? ""}</td>
        <td contenteditable data-field="boiler_set" data-id="${row.id}">${row.boiler_set ?? ""}</td>
        <td contenteditable data-field="radiator_current" data-id="${row.id}">${row.radiator_current ?? ""}</td>
        <td contenteditable data-field="radiator_set" data-id="${row.id}">${row.radiator_set ?? ""}</td>
        <td contenteditable data-field="mode" data-id="${row.id}">${row.mode ?? ""}</td>
      </tr>`;
    }
  }

  document.addEventListener("blur", async (event) => {
    if (!event.target.dataset.field) return;
    const field = event.target.dataset.field;
    const id = event.target.dataset.id;
    const value = event.target.textContent;

    await fetch(`/api/readings/${id}/edit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ [field]: value, edited_by: "adam" }),
    });
  }, true);

  loadTable();
</script>
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_edits_api.py::test_post_edit_updates_effective_values -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/api.py src/heater_reader/static/index.html src/heater_reader/db.py tests/test_edits_api.py
git commit -m "feat: add manual correction API"
```

---

### Task 11: Add CLI entrypoint for capture loop

**Files:**
- Create: `src/heater_reader/cli.py`
- Modify: `requirements.txt`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
# tests/test_cli.py
from heater_reader.cli import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.config == "config.yml"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_parse_args_defaults -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/heater_reader/cli.py
import argparse


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yml")
    return parser.parse_args(argv)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_parse_args_defaults -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/heater_reader/cli.py tests/test_cli.py

# Also add core deps for runtime
printf "fastapi\nuvicorn\npyyaml\nopencv-python\npytesseract\n" > requirements.txt

git add requirements.txt

git commit -m "feat: add cli and runtime deps"
```

---

### Task 12: Add README for run instructions

**Files:**
- Create: `README.md`
- Create: `tests/test_readme.py`

**Step 1: Write the failing test**

```python
# tests/test_readme.py
from pathlib import Path


def test_readme_mentions_config():
    text = Path("README.md").read_text()
    assert "config.yml" in text
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_readme.py::test_readme_mentions_config -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```markdown
# Boiler OCR Monitor

## Setup
1. Create a virtualenv and install requirements.
2. Create `config.yml` with camera settings.
3. Run the API: `uvicorn heater_reader.app:create_app --factory --reload`.

## Config
```

```yaml
capture:
  interval_seconds: 60
  image_root: data/images
  rtsp_url: rtsp://user:pass@camera/stream
  onvif_snapshot_url: http://camera/snapshot.jpg
```
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_readme.py::test_readme_mentions_config -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md tests/test_readme.py
git commit -m "docs: add readme"
```

---

## Plan complete and saved to `docs/plans/2026-01-31-boiler-ocr-implementation-plan.md`.

Two execution options:

1. Subagent-Driven (this session) — I dispatch fresh subagent per task, review between tasks
2. Parallel Session (separate) — open new session with executing-plans, batch execution with checkpoints

Which approach?
