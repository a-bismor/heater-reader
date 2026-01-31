from datetime import datetime, timezone
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from heater_reader.db import Database
from heater_reader.config import load_config
from pathlib import Path
from pydantic import BaseModel
import yaml

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/api/readings")
def readings(request: Request):
    db = Database(request.app.state.db_path)
    rows = db.list_effective_readings()
    return [dict(row) for row in rows]


@router.get("/")
def index():
    html = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(html.read_text())


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


class CropPayload(BaseModel):
    x: int
    y: int
    w: int
    h: int


class EditPayload(BaseModel):
    boiler_current: int | None = None
    boiler_set: int | None = None
    radiator_current: int | None = None
    radiator_set: int | None = None
    mode: str | None = None
    edited_by: str = "adam"


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


@router.post("/api/readings/{reading_id}/edit")
def edit_reading(reading_id: int, payload: EditPayload, request: Request):
    db = Database(request.app.state.db_path)
    db.insert_edit(reading_id, **payload.model_dump())
    row = db.get_effective_reading(reading_id)
    return dict(row)
