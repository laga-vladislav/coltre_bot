import asyncio
import dataclasses
import aiomysql


@dataclasses.dataclass
class Exercise:
    id: int
    name: str
    repetitions_count: int
    unit: str


async def get_exercises(loop) -> list[Exercise]:
    pool = await aiomysql.create_pool(host='localhost', port=3307,
                                      user='bot', password='sOSDGB',
                                      db='coltre', loop=loop)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * from exercise;")
            results = await cur.fetchall()
    pool.close()
    await pool.wait_closed()

    exercises = []
    for exercise in results:
        exercises.append(
            Exercise(
                id=exercise[0],
                name=exercise[1],
                repetitions_count=exercise[2],
                unit=exercise[3]
            )
        )
    print(exercises)
    # [Exercise(id=1, name='Отжимания', repetitions_count=180, unit='раз'),
    # Exercise(id=2, name='Приседания', repetitions_count=220, unit='раз'),
    # Exercise(id=3, name='Подтягивания', repetitions_count=65, unit='раз'),
    # Exercise(id=4, name='Планка', repetitions_count=12, unit='минут')]
    return exercises


loop = asyncio.get_event_loop()
loop.run_until_complete(get_exercises(loop))
