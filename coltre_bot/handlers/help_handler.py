from telebot.async_telebot import AsyncTeleBot

from coltre_bot.templates import help

async def help_handler(bot: AsyncTeleBot, chat_id: int) -> None:
    await bot.send_message(
        chat_id=chat_id,
        text=help.build_text()
    )
