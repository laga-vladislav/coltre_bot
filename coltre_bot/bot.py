import asyncio

from telebot.async_telebot import AsyncTeleBot

from handlers import start_handler, current_program_handler, help_handler

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
        async def start_command(message):
            await start_handler.start_handler(bot, message.chat.id)

        """Current program command"""
        @bot.message_handler(commands=['current_program'])
        async def current_program_command(message):
            await current_program_handler.current_program_handler(bot, message.chat.id)

        @bot.message_handler(commands=['help'])
        async def help_command(message):
            await help_handler.help_handler(bot, message.chat.id)

        asyncio.run(bot.polling())
    except Exception as e:
        print(e)
