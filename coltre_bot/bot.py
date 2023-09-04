import asyncio

from telebot.async_telebot import AsyncTeleBot

from handlers import start_handler

from coltre_bot import config

if not config.BOT_TOKEN or not config.COLTRE_CHANNEL_ID:
    raise ValueError(
        "BOT_TOKEN or CHANNEL_ID invalid"
    )


if __name__ == "__main__":
    try:
        bot = AsyncTeleBot(config.BOT_TOKEN)

        """Start command"""
        @bot.message_handler(commands=['start'])
        async def start(message):
            await start_handler.start_handler(bot, message.chat.id)

        asyncio.run(bot.polling())
    except Exception:
        import traceback

        print(traceback.format_exc())
