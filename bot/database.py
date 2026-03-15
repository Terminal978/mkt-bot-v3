import aiosqlite
import json

DB_PATH = "garden_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                coins INTEGER DEFAULT 200,
                garden_type TEXT DEFAULT 'small',
                inventory TEXT DEFAULT '{}',
                plots TEXT DEFAULT '[]',
                watering_cans INTEGER DEFAULT 1,
                last_daily TEXT DEFAULT NULL
            )
        """)
        # Добавить колонку если таблица уже существует
        try:
            await db.execute("ALTER TABLE users ADD COLUMN last_daily TEXT DEFAULT NULL")
        except Exception:
            pass
        await db.commit()

async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            if row:
                data = dict(row)
                data["inventory"] = json.loads(data["inventory"])
                data["plots"] = json.loads(data["plots"])
                return data
    return None

async def create_user(user_id: int):
    from config import GARDENS
    plots = [None] * GARDENS["small"]["slots"]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, plots) VALUES (?, ?)",
            (user_id, json.dumps(plots))
        )
        await db.commit()

async def update_user(user_id: int, **kwargs):
    if "inventory" in kwargs:
        kwargs["inventory"] = json.dumps(kwargs["inventory"])
    if "plots" in kwargs:
        kwargs["plots"] = json.dumps(kwargs["plots"])
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
        await db.commit()

async def ensure_user(user_id: int) -> dict:
    user = await get_user(user_id)
    if not user:
        await create_user(user_id)
        user = await get_user(user_id)
    return user
