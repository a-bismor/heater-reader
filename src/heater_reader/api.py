from fastapi import APIRouter, Request
from heater_reader.db import Database

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/api/readings")
def readings(request: Request):
    db = Database(request.app.state.db_path)
    rows = db.list_effective_readings()
    return [dict(row) for row in rows]

