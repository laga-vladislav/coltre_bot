from typing import Tuple, Optional

from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import TextFilter
from telebot.types import Message

from coltre_bot.core.service.training_level import get_training_levels, TrainingLevel
from coltre_bot.core.service.exercise import get_exercises
from coltre_bot.templates.renderer import render_template
from coltre_bot.handlers import keyboards


class JoiningStates(StatesGroup):
    training_level_introduce = State()
    training_level_preview = State()
    timezone = State()


class JoinHandler:
    def __init__(
            self,
            bot_instance: AsyncTeleBot,
            message: Message
    ) -> None:
        self.BOT_INSTANCE = bot_instance
        self.MESSAGE = message
        self.TRAINING_LEVELS = None

    async def build_join_handler(self) -> None:
        """
        Используется для запуска всей подпрограммы обработки команды join
        """
        await self._ask_training_level_from_user()

    async def _ask_training_level_from_user(self) -> None:
        # Работа с состояниями
        await self.BOT_INSTANCE.set_state(
            self.MESSAGE.chat.id,
            JoiningStates.training_level_introduce,
            self.MESSAGE.chat.id
        )

        self.TRAINING_LEVELS = await self._get_training_levels()

        # Получаем информацию, необходимую для отправки самого сообщения
        text, count_of_training_levels = await self._get_message_text_and_len_of_training_levels()
        keyboard_with_level_numbers = keyboards.get_numbers_keyboard(
            data=count_of_training_levels
        )

        await self.BOT_INSTANCE.send_message(
            chat_id=self.MESSAGE.chat.id,
            text=text,
            reply_markup=keyboard_with_level_numbers
        )

        # Инициализируем хендлеры для данного состояния
        await self._register_introduce_handlers(count_of_training_levels)

    @staticmethod
    async def _get_training_levels() -> list[TrainingLevel]:
        levels = await get_training_levels()
        return levels

    async def _get_message_text_and_len_of_training_levels(self) -> Tuple[str, int]:
        if self.TRAINING_LEVELS is None:
            self.TRAINING_LEVELS = await self._get_training_levels()
        rendered_text = render_template(
            "ask_for_training_level",
            {
                'training_levels': self.TRAINING_LEVELS
            }
        )
        return rendered_text, len(self.TRAINING_LEVELS)

    async def _register_introduce_handlers(self, count_of_training_levels: int) -> None:
        """
        Инициализируем хендлеры для состояния "training_level_introduce"
        """

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_introduce, is_digit=True)
        async def correct_number(new_message):
            """
            Выполняется, если пользователь ввёл нужное число
            0 < "число, введённое пользователем" <= count_of_training_levels
            """
            if 0 < int(new_message.text) <= count_of_training_levels:
                await self._correct_get_training_level_from_user(new_message)
            else:
                await self._incorrect_get_training_level_from_user(new_message)

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_introduce, is_digit=False)
        async def incorrect_number(new_message):
            """
            Выполняется, если пользователь ввёл строку
            """
            await self._incorrect_get_training_level_from_user(new_message)


    async def _correct_get_training_level_from_user(self, new_message: Message) -> None:
        # Работа с состояниями
        await self.BOT_INSTANCE.set_state(
            self.MESSAGE.chat.id,
            JoiningStates.training_level_preview,
            self.MESSAGE.chat.id
        )

        # Работа с временным хранилищем
        selected_training_level_index = int(new_message.text) - 1
        await self._retrieve_single_data(
            data_key='selected_training_level',
            data_value=self.TRAINING_LEVELS[selected_training_level_index],
            user_id=new_message.chat.id
        )

        await self._preview_training_level()


    async def _incorrect_get_training_level_from_user(self, new_message: Message) -> None:
        await self.BOT_INSTANCE.send_message(self.MESSAGE.chat.id,
                                             f"Кажется, уровня подготовки под номером '{new_message.text}' не существует")


    async def _preview_training_level(self) -> None:
        async with self.BOT_INSTANCE.retrieve_data(
                user_id=self.MESSAGE.chat.id,
                chat_id=self.MESSAGE.chat.id
        ) as data:
            exercises = await get_exercises()

            rendered_text = render_template(
                template_name="training_level_preview",
                data={
                    'training_level': data['selected_training_level'],
                    'exercises': exercises
                }
            )

            await self.BOT_INSTANCE.send_message(
                chat_id=self.MESSAGE.chat.id,
                text=rendered_text,
                reply_markup=keyboards.get_yes_or_no_keyboard(),
                parse_mode='Markdown'
            )

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_preview, text=TextFilter(equals='Да'))
        async def _preview_training_level_agree(new_message):
            await self._ask_timezone_from_user(new_message)

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_preview, text=TextFilter(equals='Нет'))
        async def _preview_training_level_disagree(new_message):
            await self._ask_training_level_from_user()


    async def _ask_timezone_from_user(self) -> None:
        pass


    async def _retrieve_single_data(
            self,
            data_key: str,
            data_value: str | int,
            user_id: int,
            chat_id: Optional[int] = None
    ) -> None:
        if chat_id is None:
            chat_id = user_id
        async with self.BOT_INSTANCE.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            print(data)
            data[data_key] = data_value
            print(data)
