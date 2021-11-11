from fastapi import FastAPI

from .routers import router

app = FastAPI()
app.include_router(router)


@app.get("/heartbeat", include_in_schema=False)
def heartbeat():
    return {"status": "OK"}
