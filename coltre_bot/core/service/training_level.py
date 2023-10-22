import asyncio

from coltre_bot.core.db import fetch_all
from coltre_bot.core.models.training_level import TrainingLevel


async def get_training_levels() -> list[TrainingLevel]:
    training_levels_sql_query = _get_training_levels_sql_query()
    results = await fetch_all(training_levels_sql_query)
    training_levels = _parse_fetch_all(results)
    return training_levels


def _get_training_levels_sql_query():
    return """SELECT * from training_level;"""


def _parse_fetch_all(results: tuple) -> list[TrainingLevel]:
    training_levels = []
    for training_level in results:
        training_levels.append(
            TrainingLevel(
                id=training_level[0],
                training_level_name=training_level[1],
                description=training_level[2],
                multiplier=training_level[3]
            )
        )
    return training_levels


async def main():
    training_levels = await get_training_levels()
    print(training_levels)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
