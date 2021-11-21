from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi_cloudauth.cognito import CognitoClaims

from starlette.requests import Request
from starlette.responses import Response

from .auth import get_current_user
from .db import client as db_client
from .schemas import TodoTaskIn, TodoTaskOut
from .models import ToDoTaskModel

router = APIRouter()


async def get_db_connection():
    async with db_client.pool.acquire() as conn:
        yield conn


@router.post(
    "/task",
    status_code=201,
    tags=["task"],
    responses={
        201: {
            "headers": {
                "location": {
                    "schema": {"type": "string"},
                    "description": "作成したタスクの参照先URL",
                    "example": "https://example.com/task/1",
                },
            },
            "content": None,
        },
        401: {"description": "Unauthorized"},
    },
)
async def create(
    request: Request,
    response: Response,
    task_form: TodoTaskIn = Body(...),
    db=Depends(get_db_connection),
    user: CognitoClaims = Depends(get_current_user),
):
    task = ToDoTaskModel(
        title=task_form.title,
        content=task_form.content,
        user=user.username,
    )
    await task.create(db)
    response.headers["location"] = f"{request.url}/{task.id}"
    return None


@router.put(
    "/task/{id}",
    tags=["task"],
    responses={
        200: {"content": None},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
    },
)
async def update(
    id: int = Path(...),
    task_form: TodoTaskIn = Body(...),
    db=Depends(get_db_connection),
    user: CognitoClaims = Depends(get_current_user),
):
    task = await ToDoTaskModel.get(db, id, user.username)
    if not task:
        raise HTTPException(status_code=404)
    task.title = task_form.title
    task.content = task_form.content
    await task.update(db)
    return None


@router.delete(
    "/task/{id}",
    tags=["task"],
    response_description="Successfully Deleted",
    responses={
        200: {"content": None},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
    },
)
async def delete(
    id: int = Path(...),
    db=Depends(get_db_connection),
    user: CognitoClaims = Depends(get_current_user),
):
    task = await ToDoTaskModel.get(db, id, user.username)
    if not task:
        raise HTTPException(status_code=404)
    await task.delete(db)
    return None


@router.get(
    "/task/_search",
    tags=["task"],
    response_model=List[TodoTaskOut],
    responses={
        200: {
            "headers": {
                "link": {
                    "schema": {"type": "string"},
                    "description": "次ページのURL",
                    "example": "<https://example.com/task/_search?page=3&count=100>; rel=next",
                },
            },
        },
        401: {"description": "Unauthorized"},
    },
)
async def search(
    request: Request,
    response: Response,
    q: str = Query(..., min_length=1, max_length=100, description="検索文字"),
    count: int = Query(100, ge=1, le=100, description="検索結果の最大件数"),
    page: int = Query(1, ge=1, description="ページ数"),
    db=Depends(get_db_connection),
    user: CognitoClaims = Depends(get_current_user),
):
    offset = count * (page - 1)
    limit = count + 1  # add 1 object to check next page
    tasks = await ToDoTaskModel.search(db, q, user.username, offset, limit)

    # build response header `link`
    response.headers["link"] = ""
    if len(tasks) > count:
        tasks = tasks[:-1]
        response.headers[
            "link"
        ] += f'<{request.url}?q={q}&count={count}&page={page + 1}>; rel="next"'

    return [TodoTaskOut(id=t.id, title=t.title, content=t.content) for t in tasks]


@router.get(
    "/task/{id}",
    tags=["task"],
    response_model=TodoTaskOut,
    responses={404: {"description": "Not found"}},
)
async def get(
    id: int = Path(...),
    db=Depends(get_db_connection),
    user: CognitoClaims = Depends(get_current_user),
):
    task = await ToDoTaskModel.get(db, id, user.username)
    if not task:
        raise HTTPException(status_code=404)
    return TodoTaskOut(id=id, title=task.title, content=task.content)
