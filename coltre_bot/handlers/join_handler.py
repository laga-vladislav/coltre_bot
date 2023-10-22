from telebot import custom_filters
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from coltre_bot.core.service.training_level import get_training_levels
from coltre_bot.templates.renderer import render_template

class JoiningStates(StatesGroup):
    training_level_introduce = State()
    training_level_preview = State()
    timezone = State()

async def join_handler(bot_instance: AsyncTeleBot, message: Message) -> None:
    await _get_training_level_from_user(bot_instance, message.chat.id)

async def _get_training_level_from_user(bot_instance: AsyncTeleBot, user_id: int):
    await bot_instance.set_state(user_id, JoiningStates.training_level_introduce, user_id)

    training_levels = await get_training_levels()
    rendered_text = render_template(
        "ask_for_training_level",
        {
            'training_levels': training_levels
        }
    )

    await bot_instance.send_message(user_id, rendered_text)
