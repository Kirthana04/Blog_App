import os
from dotenv import load_dotenv
import asyncpg
from fastapi import FastAPI

load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('db_user')}:{os.getenv('db_password')}"
    f"@{os.getenv('db_host')}:{os.getenv('db_port')}/{os.getenv('db_name')}"
)

app = FastAPI()

async def get_db_pool():
    if not hasattr(app.state, "db_pool"):
        app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
    return app.state.db_pool

async def init_db():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("CREATE SCHEMA IF NOT EXISTS blogschema")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blogschema.users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blogschema.blogs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES blogschema.users(id),
                title TEXT NOT NULL,
                description TEXT,
                image TEXT,  -- Changed from BYTEA to TEXT
                tags TEXT[],
                contents TEXT,
                deleted_flag BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """
        )
        
