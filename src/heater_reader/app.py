from fastapi import FastAPI
from heater_reader.api import router
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
