import logging
import uvicorn
from fastapi import FastAPI
from nicegui import ui

# from password_manager import app
from password_manager.app import api


logging.basicConfig(level=logging.DEBUG)  # https://stackoverflow.com/a/57234760

fastapi_app = FastAPI()
fastapi_app.include_router(api.router)

ui.run_with(fastapi_app, storage_secret="todo, a real secret")

# if __name__ in {"__main__", "__mp_main__"}:
if __name__ == "__main__":
    uvicorn.run("main:fastapi_app", log_level="info", reload=True)
