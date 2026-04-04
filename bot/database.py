import asyncpg
import json
import os

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        db_url = os.environ["DATABASE_URL"].replace("postgres://", "postgresql://", 1)
        _pool = await asyncpg.create_pool(db_url, command_timeout=10, min_size=1, max_size=5)
    return _pool

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                coins INTEGER DEFAULT 200,
                garden_type TEXT DEFAULT 'small',
                inventory TEXT DEFAULT '{}',
                plots TEXT DEFAULT '[]',
                watering_cans INTEGER DEFAULT 1,
                last_daily TEXT DEFAULT NULL
            )
        """)

async def get_user(user_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if row:
            data = dict(row)
            data["inventory"] = json.loads(data["inventory"])
            data["plots"] = json.loads(data["plots"])
            return data
    return None

async def create_user(user_id: int):
    from config import GARDENS
    plots = [None] * GARDENS["small"]["slots"]
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id, plots) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_id, json.dumps(plots)
        )

async def update_user(user_id: int, **kwargs):
    if "inventory" in kwargs:
        kwargs["inventory"] = json.dumps(kwargs["inventory"])
    if "plots" in kwargs:
        kwargs["plots"] = json.dumps(kwargs["plots"])
    fields = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(kwargs))
    values = [user_id] + list(kwargs.values())
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE users SET {fields} WHERE user_id = $1", *values)

async def ensure_user(user_id: int) -> dict:
    user = await get_user(user_id)
    if not user:
        await create_user(user_id)
        user = await get_user(user_id)
    return user
