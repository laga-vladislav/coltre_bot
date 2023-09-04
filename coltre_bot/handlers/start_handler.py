from telebot.async_telebot import AsyncTeleBot

from coltre_bot.templates import start

async def start_handler(bot: AsyncTeleBot, chat_id: int) -> None:
    await bot.send_message(
        chat_id=chat_id,
        text=start.TEXT
    )
