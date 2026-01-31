from datetime import datetime, timezone
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from heater_reader.db import Database
from pathlib import Path

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
