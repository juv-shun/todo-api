from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query

from starlette.requests import Request
from starlette.responses import Response

from .db import client as db_client
from .schemas import TodoTaskIn, TodoTaskOut
from .models import ToDoTaskModel

router = APIRouter()


async def get_db_connection():
    async with db_client.pool.acquire() as conn:
        yield conn


@router.post("/task", status_code=201)
async def create(
    request: Request,
    response: Response,
    task_form: TodoTaskIn = Body(...),
    db=Depends(get_db_connection),
):
    user = "shun"
    task = ToDoTaskModel(
        title=task_form.title,
        content=task_form.content,
        user=user,
    )
    await task.create(db)
    response.headers["location"] = f"{request.url}/{task.id}"
    return None


@router.put("/task/{task_id}")
async def update(
    task_id: int = Path(...),
    task_form: TodoTaskIn = Body(...),
    db=Depends(get_db_connection),
):
    user = "shun"
    task = await ToDoTaskModel.get(db, task_id, user)
    if not task:
        raise HTTPException(status_code=404)
    task.title = task_form.title
    task.content = task_form.content
    await task.update(db)
    return None


@router.delete("/task/{task_id}")
async def delete(
    task_id: int = Path(...),
    db=Depends(get_db_connection),
):
    user = "shun"
    task = await ToDoTaskModel.get(db, task_id, user)
    if not task:
        raise HTTPException(status_code=404)
    await task.delete(db)
    return None


@router.get("/task/_search")
async def search(
    request: Request,
    response: Response,
    q: str = Query(..., min_length=1, max_length=100),
    count: int = Query(100, ge=1, le=100),
    page: int = Query(1, ge=1),
    db=Depends(get_db_connection),
):
    user: str = "shun"
    offset = count * (page - 1)
    limit = count + 1  # add 1 object to check next page
    tasks = await ToDoTaskModel.search(db, q, user, offset, limit)

    # build response header `link`
    response.headers["link"] = ""
    if len(tasks) > count:
        tasks = tasks[:-1]
        response.headers["link"] += f'<{request.url}?q={q}&count={count}&page={page + 1}>; rel="next"'

    return [TodoTaskOut(id=t.id, title=t.title, content=t.content) for t in tasks]


@router.get("/task/{task_id}")
async def get(
    task_id: int = Path(...),
    db=Depends(get_db_connection),
):
    user = "shun"
    task = await ToDoTaskModel.get(db, task_id, user)
    if not task:
        raise HTTPException(status_code=404)
    return TodoTaskOut(id=task_id, title=task.id, conent=task.content)
