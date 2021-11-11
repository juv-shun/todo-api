import asyncpg


class DB:
    async def init(self, host: str, user: str, password: str, db: str) -> None:
        self.pool = await asyncpg.create_pool(
            host=host,
            user=user,
            password=password,
            database=db,
        )

    async def close(self) -> None:
        await self.pool.close()


client = DB()
