import asyncio

from telebot.async_telebot import AsyncTeleBot
from telebot.storage import StateMemoryStorage

from handlers import base_handler_with_templates, current_program_handler, join_handler

from coltre_bot import config

if not config.BOT_TOKEN or not config.COLTRE_CHANNEL_ID:
    raise ValueError(
        "BOT_TOKEN or CHANNEL_ID invalid"
    )

if __name__ == "__main__":
    try:
        registration_storage = StateMemoryStorage()
        bot = AsyncTeleBot(config.BOT_TOKEN, registration_storage)
        """Start command"""
        @bot.message_handler(commands=['start'])
        async def start_command(message):
            await base_handler_with_templates.base_handler(
                bot_instance=bot,
                chat_id=message.chat.id,
                command_name='start')

        """Current program command"""
        @bot.message_handler(commands=['current_program'])
        async def current_program_command(message):
            await current_program_handler.current_program_handler(bot, message.chat.id)

        """Help command"""
        @bot.message_handler(commands=['help'])
        async def help_command(message):
            await base_handler_with_templates.base_handler(
                bot_instance=bot,
                chat_id=message.chat.id,
                command_name='help')

        asyncio.run(bot.polling())
    except Exception as e:
        print(e)
