import asyncio

from telebot import asyncio_filters
from telebot.asyncio_filters import TextMatchFilter
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from handlers import base_handler_with_templates, current_program_handler, join_handler

from coltre_bot import config

if not config.BOT_TOKEN or not config.COLTRE_CHANNEL_ID:
    raise ValueError(
        "BOT_TOKEN or CHANNEL_ID invalid"
    )

if __name__ == "__main__":
    try:

        bot = AsyncTeleBot(token=config.BOT_TOKEN, state_storage=StateMemoryStorage())

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

        """Join"""
        @bot.message_handler(commands=['join'])
        async def join_command(message):
            await join_handler.join_handler(bot, message)


        bot.add_custom_filter(asyncio_filters.StateFilter(bot))
        bot.add_custom_filter(asyncio_filters.IsDigitFilter())
        bot.add_custom_filter(TextMatchFilter())

        asyncio.run(bot.polling())
    except Exception as e:
        print(e)
