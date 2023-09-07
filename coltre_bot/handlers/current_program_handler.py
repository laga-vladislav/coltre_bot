from telebot.async_telebot import AsyncTeleBot

from coltre_bot.templates import current_program

async def current_program_handler(bot: AsyncTeleBot, chat_id: int) -> None:
    await bot.send_message(
        chat_id=chat_id,
        text=await current_program.build_text()
    )
