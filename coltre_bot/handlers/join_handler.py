import pytz
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from datetime import datetime

from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import TextFilter
from telebot.types import Message

from coltre_bot.core.service.training_level import get_training_levels, TrainingLevel
from coltre_bot.core.service.exercise import get_exercises
from coltre_bot.templates.renderer import render_template
from coltre_bot.handlers import keyboards
from coltre_bot.exceptions import WrongMonthDigit


class JoiningStates(StatesGroup):
    training_level_request = State()
    training_level_preview = State()
    timezone_request = State()
    timezone_preview = State()


class StateController:
    """
    TODO вынести часть этого класса в базовый, реализовать наследование
    """

    def __init__(self, bot_instance: AsyncTeleBot, user_id: int, chat_id: Optional[int] = None):
        self.BOT_INSTANCE = bot_instance
        if chat_id is None:
            chat_id = user_id
        self.USER_ID = user_id
        self.CHAT_ID = chat_id

    async def set_training_level_request(self) -> None:
        await self.BOT_INSTANCE.set_state(
            self.USER_ID,
            JoiningStates.training_level_request,
            self.CHAT_ID
        )

    async def set_training_level_preview(self) -> None:
        await self.BOT_INSTANCE.set_state(
            self.USER_ID,
            JoiningStates.training_level_preview,
            self.CHAT_ID
        )

    async def set_timezone_request(self) -> None:
        await self.BOT_INSTANCE.set_state(
            self.USER_ID,
            JoiningStates.timezone_request,
            self.CHAT_ID
        )

    async def set_timezone_preview(self) -> None:
        await self.BOT_INSTANCE.set_state(
            self.USER_ID,
            JoiningStates.timezone_preview,
            self.CHAT_ID
        )


class BaseJoinSubHandler(ABC):
    def __init__(self, bot_instance: AsyncTeleBot, user_id: int):
        self.BOT_INSTANCE = bot_instance
        self.USER_ID = user_id
        self.STATE_CONTROLLER = StateController(bot_instance, user_id)

    @abstractmethod
    async def ask(self):
        pass

    @abstractmethod
    async def _exit_subprogram(self):
        pass

    @abstractmethod
    async def _register_handlers(self):
        pass


class TrainingLevelSubprogram(BaseJoinSubHandler):
    def __init__(self, bot_instance: AsyncTeleBot, user_id: int):
        self.TRAINING_LEVELS: list[TrainingLevel] = []
        self.SELECTED_TRAINING_LEVEL_INDEX: int = None
        super().__init__(bot_instance, user_id)

    async def ask(self):
        await self._register_handlers()
        await self._training_level_request()

    async def _training_level_request(self):
        await self.STATE_CONTROLLER.set_training_level_request()
        self.TRAINING_LEVELS = await get_training_levels()

        text, count_of_training_levels = await self._get_message_text_and_len_of_training_levels()
        keyboard_with_level_numbers = keyboards.get_numbers_keyboard(
            data=count_of_training_levels
        )

        await self.BOT_INSTANCE.send_message(
            chat_id=self.USER_ID,
            text=text,
            reply_markup=keyboard_with_level_numbers
        )

    async def _get_message_text_and_len_of_training_levels(self) -> Tuple[str, int]:
        rendered_text = render_template(
            "ask_for_training_level",
            {
                'training_levels': self.TRAINING_LEVELS
            }
        )
        return rendered_text, len(self.TRAINING_LEVELS)

    async def _training_level_preview(self, message_text: str):
        await self.STATE_CONTROLLER.set_training_level_preview()
        self.SELECTED_TRAINING_LEVEL_INDEX = int(message_text) - 1

        exercises = await get_exercises()

        rendered_text = render_template(
            template_name="training_level_preview",
            data={
                'training_level': self.TRAINING_LEVELS[self.SELECTED_TRAINING_LEVEL_INDEX],
                'exercises': exercises
            }
        )

        await self.BOT_INSTANCE.send_message(
            chat_id=self.USER_ID,
            text=rendered_text,
            reply_markup=keyboards.get_yes_or_no_keyboard(),
            parse_mode='Markdown'
        )

    async def _incorrect_get_training_level_from_user(self, message_text: str):
        await self.BOT_INSTANCE.send_message(self.USER_ID,
                                             f"Кажется, уровня подготовки под номером '{message_text}' не существует")

    async def _exit_subprogram(self):
        async with self.BOT_INSTANCE.retrieve_data(user_id=self.USER_ID, chat_id=self.USER_ID) as data:
            data['selected_training_level'] = self.TRAINING_LEVELS[self.SELECTED_TRAINING_LEVEL_INDEX]
            print(data)
        await TimezoneSubprogram(self.BOT_INSTANCE, self.USER_ID).ask()

    async def _register_handlers(self):
        """
        Инициализируем все хендлеры
        """

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_request, is_digit=True)
        async def correct_number(new_message: Message):
            """
            Выполняется, если пользователь ввёл нужное число
            0 < "число, введённое пользователем" <= count_of_training_levels
            """
            if 0 < int(new_message.text) <= len(self.TRAINING_LEVELS):
                await self._training_level_preview(new_message.text)
            else:
                await self._incorrect_get_training_level_from_user(new_message.text)

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_request, is_digit=False)
        async def incorrect_number(new_message: Message):
            """
            Выполняется, если пользователь ввёл строку
            """
            await self._incorrect_get_training_level_from_user(new_message.text)

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_preview, text=TextFilter(equals='Да'))
        async def agree(new_message: Message):
            await self._exit_subprogram()

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.training_level_preview, text=TextFilter(equals='Нет'))
        async def disagree(new_message: Message):
            await self._training_level_request()


class TimezoneSubprogram(BaseJoinSubHandler):
    def __init__(self, bot_instance: AsyncTeleBot, user_id: int):
        self.SELECTED_TIMEZONE: int = None
        super().__init__(bot_instance, user_id)

    async def ask(self):
        await self._register_handlers()

        await self._timezone_request()

    async def _timezone_request(self):
        current_state = await self.BOT_INSTANCE.get_state(
            user_id=self.USER_ID)  # пометка: get_state всегда возвращает строку.

        if current_state == 'JoiningStates:timezone_request':
            await self.BOT_INSTANCE.send_message(chat_id=self.USER_ID, text='Кажется, что-то пошло не так')
        else:
            await self.STATE_CONTROLLER.set_timezone_request()

        rendered_text = render_template(template_name='ask_for_timezone')

        await self.BOT_INSTANCE.send_message(
            chat_id=self.USER_ID,
            text=rendered_text,
            reply_markup=keyboards.delete_keyboad()
        )

    async def _timezone_preview(self, message_text: str):
        await self.STATE_CONTROLLER.set_timezone_preview()

        datetime_text = get_datetime_text(message_text)

        rendered_text = render_template(
            'timezone_preview',
            {
                'user_timezone': message_text,
                'user_datetime': datetime_text
            }
        )

        await self.BOT_INSTANCE.send_message(
            chat_id=self.USER_ID,
            text=rendered_text,
            reply_markup=keyboards.get_yes_or_no_keyboard()
        )

        self.SELECTED_TIMEZONE = int(message_text)

    async def _exit_subprogram(self):
        async with self.BOT_INSTANCE.retrieve_data(user_id=self.USER_ID, chat_id=self.USER_ID) as data:
            data['selected_timezone'] = self.SELECTED_TIMEZONE
            print(data)

    async def _register_handlers(self):
        @self.BOT_INSTANCE.message_handler(state=JoiningStates.timezone_request, is_digit=True)
        async def correct(new_message: Message):
            if is_russian_utc(new_message.text):
                await self._timezone_preview(new_message.text)
            else:
                await self._timezone_request()

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.timezone_request, is_digit=False)
        async def incorrect(new_message: Message):
            await self._timezone_request()

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.timezone_preview, text=TextFilter(equals='Да'))
        async def agree(new_message: Message):
            await self._exit_subprogram()

        @self.BOT_INSTANCE.message_handler(state=JoiningStates.timezone_preview, text=TextFilter(equals='Нет'))
        async def disagree(new_message: Message):
            await self._timezone_request()


class JoinHandler:
    def __init__(
            self,
            bot_instance: AsyncTeleBot,
            message: Message
    ) -> None:
        self.BOT_INSTANCE = bot_instance
        self.MESSAGE = message

    async def build_join_handler(self) -> None:
        """
        Используется для запуска всей подпрограммы обработки команды join
        TrainingLevelSubprogram запускает TimezoneSubprogram
        """
        training_level_handler = TrainingLevelSubprogram(
            bot_instance=self.BOT_INSTANCE,
            user_id=self.MESSAGE.chat.id
        )
        await training_level_handler.ask()


"""
TODO: Вынести функционал работы с часовыми поясами в отдельный сервис
"""
def is_russian_utc(value: str | int) -> bool:
    try:
        timezones = [timezone for timezone in range(2, 13)]
        if int(value) in timezones:
            return True
        return False
    except ValueError:
        return False


def _get_full_datetime_with_timezone(value: str | int) -> datetime | None:
    """
    Формат вывода:
    2023-10-27 12:51:56.731499+09:00
    """
    if is_russian_utc(value):
        desired_timezone = pytz.FixedOffset(int(value) * 60)
        current_time = datetime.now(desired_timezone)
        return current_time
    return None


def get_datetime_text(timezone_value: str | int) -> str:
    """
    Формат вывода:
    12:50. Октябрь, 20 число
    """
    datetime_value = _get_full_datetime_with_timezone(timezone_value)
    time = datetime_value.time().strftime("%H:%M")
    date = datetime_value.date().strftime("%d %m")
    day, month_digit = date.split(' ')
    month_text = _convert_digit_to_month(month_digit)
    datetime_text = f"{time}. {_to_upper_first_letter(month_text)}, {day} число"
    return datetime_text


def _to_upper_first_letter(text: str) -> str:
    try:
        return text[0].upper() + text[1::]
    except IndexError:
        return text


def _convert_digit_to_month(month_digit: int | str) -> str:
    month_digit = int(month_digit)
    try:
        if not (0 < month_digit < 13):
            raise WrongMonthDigit(f'Месяца под номером {month_digit} не существует')
        month_names = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь',
                       'ноябрь', 'декабрь']
        return month_names[month_digit - 1]
    except ValueError:
        raise WrongMonthDigit(f'"{month_digit}" не является номером месяца')


if __name__ == '__main__':
    pass
