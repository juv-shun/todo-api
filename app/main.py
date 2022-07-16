import logging
import os

from fastapi import FastAPI, Request

from .routers import router
from .db import client as db
from ._logger import init_logger

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO")

init_logger()
logger = logging.getLogger("fastapi")
logger.setLevel(APP_LOG_LEVEL)

app = FastAPI(
    title="ToDo Application Sample",
    version="0.1.0",
    description="ToDoタスクを管理するAPI。認証はCognitoユーザプールのID Tokenを検証する。",
)
app.include_router(router, prefix="/v1")


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


@app.middleware("http")
async def error_handle(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception(
            exc,
            extra={
                "client_ip": getattr(request.client, "host"),
                "user-agent": request.headers.get("user-agent"),
                "path": request.url.path,
                "method": request.method,
                "query": request.url.query,
                "body": (await request.body()).decode(),
            }
        )
        raise


@app.get("/heartbeat", include_in_schema=False)
def heartbeat():
    return {"status": "OK"}
