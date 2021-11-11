import logging
import os

from fastapi import FastAPI
from fastapi.logger import logger

from .routers import router
from .db import client as db

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO")

handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(APP_LOG_LEVEL)

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def db_startup() -> None:
    await db.init(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )
    logger.info("DB client successfully connected.")


@app.on_event("shutdown")
async def db_shutdown() -> None:
    await db.close()
    logger.info("DB client successfully closed.")


@app.get("/heartbeat", include_in_schema=False)
def heartbeat():
    return {"status": "OK"}
