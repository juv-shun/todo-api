from __future__ import annotations

from typing import List, Optional

from asyncpg.pool import PoolConnectionProxy


class ToDoTaskModel:
    def __init__(
        self,
        title: str,
        content: Optional[str],
        user: str,
        id: Optional[int] = None,
    ) -> None:
        self.id = id
        self.title = title
        self.content = content
        self.user = user

    async def create(self, conn: PoolConnectionProxy) -> None:
        if self.id is not None:
            raise ValueError("id attribute must be null.")
        sql = "INSERT INTO tasks (title, content, username) VALUES ($1, $2, $3)"
        await conn.execute(sql, self.title, self.content, self.user)
        self.id = await conn.fetchval("SELECT lastval()")
        return

    async def update(self, conn: PoolConnectionProxy) -> None:
        if self.id is None:
            raise ValueError("id attribute must not be null.")
        sql = "UPDATE tasks SET title = $1, content = $2, updated = NOW() WHERE id = $3 and username = $4"
        await conn.execute(sql, self.title, self.content, self.id, self.user)
        return

    async def delete(self, conn: PoolConnectionProxy) -> None:
        if self.id is None:
            raise ValueError("id attribute must be null.")
        sql = "DELETE FROM tasks WHERE id = $1 and username = $2"
        await conn.execute(sql, self.id, self.user)
        return

    @classmethod
    async def get(cls, conn: PoolConnectionProxy, id: int, user: str) -> Optional[ToDoTaskModel]:
        sql = "SELECT title, content FROM tasks WHERE id = $1 and username = $2"
        row = await conn.fetchrow(sql, id, user)
        return ToDoTaskModel(id=id, title=row["title"], content=row["content"], user=user) if row else None

    @classmethod
    async def search(cls, conn: PoolConnectionProxy, q: str, user: str, offset: int, limit: int) -> List[ToDoTaskModel]:
        sql = """
        SELECT id, title, content
        FROM tasks
        WHERE CONCAT(title, content) LIKE $1 AND username = $2
        ORDER BY id DESC LIMIT $3 OFFSET $4
        """
        rows = await conn.fetch(sql, f"%{q}%", user, limit, offset)
        return [ToDoTaskModel(id=row["id"], title=row["title"], content=row["content"], user=user) for row in rows]
