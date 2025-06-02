import os
import asyncpg
from fastapi import FastAPI
from dotenv import load_dotenv

# NEW → pgvector adapter
from pgvector.asyncpg import register_vector

load_dotenv()


async def init_connection(conn):
    """Initialize each connection with pgvector and set correct schema."""
    # Set search path to include whereisthisplace schema
    await conn.execute("SET search_path TO whereisthisplace, public;")
    # Register pgvector types
    await register_vector(conn)


async def init_db(app: FastAPI):
    """
    Initialise a connection pool and attach it to the FastAPI app.

    The `register_vector` callback tells asyncpg how to decode/encode
    the Postgres `vector` type (provided by the pgvector extension).
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    # `init=` is run once for every new connection in the pool
    app.state.pool = await asyncpg.create_pool(
        dsn=database_url,
        init=init_connection,     # ← updated to use our custom init function
        # optional pool sizing (tweak to your needs)
        # min_size=1,
        # max_size=10,
    )
    return app.state.pool


async def close_db(app: FastAPI):
    """Close the connection pool stored on the FastAPI app."""
    pool = getattr(app.state, "pool", None)
    if pool is not None:
        await pool.close()