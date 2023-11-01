import asyncio

from telebot.async_telebot import AsyncTeleBot

from coltre_bot.templates import renderer
from coltre_bot.handlers import keyboards


async def base_handler(bot_instance: AsyncTeleBot, chat_id: int, command_name: str) -> None:
    """Хендлер, который обрабатывает простые команды, не требующие ответа или запроса в БД"""
    rendered_text = renderer.render_template(command_name)
    await bot_instance.send_message(
        chat_id=chat_id,
        text=rendered_text,
        reply_markup=keyboards.delete_keyboad()
    )

async def main():
    print(renderer.render_template('start'))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())