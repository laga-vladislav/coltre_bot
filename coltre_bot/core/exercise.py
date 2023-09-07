import asyncio
import dataclasses

from coltre_bot.core.db import fetch_all


@dataclasses.dataclass
class Exercise:
    id: int
    name: str
    repetitions_count: int
    unit: str


async def get_exercises() -> list[Exercise]:
    exercise_sql_query = _get_exercise_sql_query()
    results = await fetch_all(exercise_sql_query)

    exercises = _parse_fetch_all(results)
    print(exercises)

    return exercises


def _get_exercise_sql_query():
    return """
        SELECT * from exercise;
    """


def _parse_fetch_all(results: tuple) -> list[Exercise]:
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
    return exercises


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_exercises())
