import asyncio
import aiomysql

from coltre_bot import config, exceptions


async def fetch_all(sql_query: str) -> tuple:
    pool = await _create_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql_query)
            results = await cur.fetchall()
    pool.close()
    await pool.wait_closed()
    return results


async def fetch_one(sql_query: str) -> tuple:
    pool = await _create_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql_query)
            (r,) = await cur.fetchone()
    pool.close()
    await pool.wait_closed()
    return r


async def insert_data(sql_query: str) -> None:
    """
    Возможные ошибки:
    aiomysql.IntegrityError (неуникальный ключевой элемент)
    """
    await execute_and_commit(sql_query)


async def delete_data(sql_query: str) -> None:
    await execute_and_commit(sql_query)


async def execute_and_commit(sql_query: str) -> None:
    pool = await _create_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql_query)
            await conn.commit()
    pool.close()
    await pool.wait_closed()


async def _create_pool() -> aiomysql.pool:
    pool = await aiomysql.create_pool(host=config.DB_HOST, port=config.DB_PORT,
                                      user=config.DB_USERNAME, password=config.DB_PASSWORD,
                                      db=config.DB_NAME, loop=asyncio.get_running_loop())
    return pool


async def main():
    # from coltre_bot.core.service.user import _register_user_sql_query, User
    # user = User(
    #     user_id=1,
    #     first_name='ne 1'
    # )
    # sql = _register_user_sql_query(user)
    # print(sql)
    # await insert_data(sql)
    # res = await fetch_one("select training_level_id from user where user_id=1;")
    # print(res)
    await insert_data("INSERT INTO membership_request (user_id) VALUES (2);")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
