from fastapi import APIRouter
from fastapi.logger import logger

router = APIRouter()


@router.get("/")
async def hello():
    logger.info("Hello World.")
    return {"message": "Hello World."}
