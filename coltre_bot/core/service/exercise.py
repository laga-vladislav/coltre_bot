import asyncio

from coltre_bot.core.db import fetch_all
from coltre_bot.core.models.exercise import Exercise


async def get_exercises() -> list[Exercise]:
    exercise_sql_query = _get_exercise_sql_query()
    results = await fetch_all(exercise_sql_query)

    exercises = _parse_fetch_all(results)
    return exercises


def _get_exercise_sql_query():
    return """SELECT * from exercise;"""


def _parse_fetch_all(results: tuple) -> list[Exercise]:
    exercises = []
    for exercise in results:
        exercises.append(
            Exercise(
                id=exercise[0],
                name=exercise[1],
                norm=exercise[3],
                unit=exercise[4]
            )
        )
    return exercises


async def main():
    exercises = await get_exercises()
    print(exercises)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
