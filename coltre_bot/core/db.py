import asyncio
import aiomysql

from coltre_bot import config

async def fetch_all(sql_query: str) -> tuple:
    pool = await _create_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql_query)
            results = await cur.fetchall()
    pool.close()
    await pool.wait_closed()
    return results

async def _create_pool() -> aiomysql.pool:
    pool = await aiomysql.create_pool(host=config.DB_HOST, port=config.DB_PORT,
                                      user=config.DB_USERNAME, password=config.DB_PASSWORD,
                                      db=config.DB_NAME, loop=asyncio.get_running_loop())
    return pool
