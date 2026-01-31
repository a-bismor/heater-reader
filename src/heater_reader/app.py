from fastapi import FastAPI
from heater_reader.api import router


def create_app(db_path: str) -> FastAPI:
    app = FastAPI()
    app.state.db_path = db_path
    app.include_router(router)
    return app
