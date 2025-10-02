from contextlib import asynccontextmanager
from typing import AsyncGenerator

from psycopg import AsyncConnection

from app.core.config_setup import CONN_STRING


async def get_db() -> AsyncGenerator[AsyncConnection, None]:
    async with await AsyncConnection.connect(CONN_STRING) as conn:
        try:
            yield conn
        finally:
            await conn.close()
