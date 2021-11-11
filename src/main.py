import logging
import os

from fastapi import FastAPI
from fastapi.logger import logger

from .routers import router

APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO")

handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(APP_LOG_LEVEL)

app = FastAPI()
app.include_router(router)


@app.get("/heartbeat", include_in_schema=False)
def heartbeat():
    return {"status": "OK"}
