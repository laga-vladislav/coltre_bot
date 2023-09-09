import asyncio

from coltre_bot.core import exercise

async def build_text() -> str:
    """Формируем сообщение со всеми упражнениями"""
    exercises = await _get_exercises()
    text = "На данный момент наша программа состоит из следующих упражнений:\n\n"
    for index, exercise_instance in enumerate(exercises):
        text += f"{index + 1}. {exercise_instance.name} — " \
                f"{exercise_instance.repetitions_count} {exercise_instance.unit}\n"

    """Временно проставляем данные о выходных вручную"""
    text += "Два выходных дня и по-новой!"
    return text

async def _get_exercises() -> list[exercise.Exercise]:
    exercises = await exercise.get_exercises()
    return exercises


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(build_text())
