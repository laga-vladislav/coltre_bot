import pytz
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from datetime import datetime

from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import TextFilter
from telebot.types import Message

from coltre_bot.core.service.user import is_group_member
from coltre_bot.core.service.training_level import get_training_levels, TrainingLevel
from coltre_bot.core.service.exercise import get_exercises, Exercise
from coltre_bot.templates.renderer import render_template
from coltre_bot.handlers import keyboards
from coltre_bot.exceptions import WrongMonthDigit


def validate_user(handler):
    async def wrapper(bot, message):
        if not await is_group_member(message.chat.id):
            await bot.send_message(
                chat_id=message.chat.id,
                text="Вы уже находитесь в группе, поэтому не можете использовать команду /join",
                reply_markup=keyboards.delete_keyboad()
            )
            return
        await handler(bot, message)

    return wrapper


# оставлю на лучшие времена
# @validate_user
async def join_handler(bot, message):
    await register_handlers(bot)
    await TrainingLevelSubprogram(bot_instance=bot).ask(message)


class JoiningStates(StatesGroup):
    """Состояния пользователя"""
    training_level_request = State()  # запрос номера уровня подготовки от пользователя
    training_level_preview = State()  # предпросмотр данных для определённого уровня подготовки
    timezone_request = State()  # запрос часового пояса от пользователя
    timezone_preview = State()  # предпросмотр даты и времени по полученном часовому поясу пользователя


class StateController:
    """Управляет состояниями пользователя"""

    def __init__(self, bot_instance: AsyncTeleBot):
        self.BOT_INSTANCE = bot_instance

    async def set_training_level_request(self, user_id: int) -> None:
        await self.BOT_INSTANCE.set_state(
            user_id,
            JoiningStates.training_level_request
        )

    async def set_training_level_preview(self, user_id: int) -> None:
        await self.BOT_INSTANCE.set_state(
            user_id,
            JoiningStates.training_level_preview
        )

    async def set_timezone_request(self, user_id: int) -> None:
        await self.BOT_INSTANCE.set_state(
            user_id,
            JoiningStates.timezone_request
        )

    async def set_timezone_preview(self, user_id: int) -> None:
        await self.BOT_INSTANCE.set_state(
            user_id,
            JoiningStates.timezone_preview
        )


class BaseJoinSubprogram(ABC):
    """Абстрактный класс подпрограмм join handler'а"""

    def __init__(self, bot_instance: AsyncTeleBot):
        self.STATE_CONTROLLER = StateController(bot_instance)
        self.BOT_INSTANCE = bot_instance

    @abstractmethod
    async def ask(self, message: Message):
        """Точка входа в подпрограмму"""
        pass

    async def get_user_data(self, user_id: int) -> dict:
        """Получаем все данных из временного хранилища пользователя"""
        async with self.BOT_INSTANCE.retrieve_data(user_id=user_id) as data:
            return data

    async def set_new_user_data(self, user_id: int, new_data: dict):
        """Перезаписывает данные во временном хранилище пользователя"""
        async with self.BOT_INSTANCE.retrieve_data(user_id=user_id) as data:
            data = new_data

    @abstractmethod
    async def exit_subprogram(self, message: Message):
        """Точка выхода из подпрограммы"""
        pass


class TrainingLevelSubprogram(BaseJoinSubprogram):
    """
    Используется для получения уровня подготовки от пользователя.
    Данные о выбранном пользователем уровне подготовки сохраняются
    во временном хранилище.
    """

    async def ask(self, message: Message):
        """Существует как входная точка в join хендлеры для более удобного использования
        в других местах программы. Аналогична training_level_request()"""
        await self.training_level_request(message)

    async def training_level_request(self, message: Message, training_levels: Optional[list[TrainingLevel]] = None):
        """Запуск процесса запрашивания уровня подготовки от пользователя"""
        await self.STATE_CONTROLLER.set_training_level_request(message.chat.id)

        training_levels = await self._check_or_get_training_levels(training_levels)

        text = self._get_message_text_training_level_request(training_levels)
        count_of_training_levels = len(training_levels)

        keyboard_with_level_numbers = keyboards.get_numbers_keyboard(
            data=count_of_training_levels
        )

        await self.BOT_INSTANCE.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard_with_level_numbers
        )

    @staticmethod
    def _get_message_text_training_level_request(training_levels: list[TrainingLevel]) -> Tuple[str, int]:
        """Возвращает отрендеренный текст для запроса уровня подготовки"""
        rendered_text = render_template(
            "training_level_request",
            {
                'training_levels': training_levels
            }
        )
        return rendered_text

    async def training_level_preview(self, message: Message, training_levels: list[TrainingLevel]):
        """Запуск процесса предпросмотра уровня подготовки для пользователя"""
        await self.STATE_CONTROLLER.set_training_level_preview(message.chat.id)

        selected_training_level = training_levels[int(message.text) - 1]
        await self._set_selected_training_level(message.chat.id, selected_training_level)

        exercises = await get_exercises()

        rendered_text = self._get_message_text_training_level_preview(selected_training_level, exercises)

        await self.BOT_INSTANCE.send_message(
            chat_id=message.chat.id,
            text=rendered_text,
            reply_markup=keyboards.get_yes_or_no_keyboard(),
            parse_mode='Markdown'
        )

    @staticmethod
    def _get_message_text_training_level_preview(selected_training_level: TrainingLevel, exercises: list[Exercise]):
        """Возвращает отрендеренный текст для предпросмотра уровня подготовки"""
        return render_template(
            template_name="training_level_preview",
            data={
                'training_level': selected_training_level,
                'exercises': exercises
            }
        )

    async def incorrect_get_training_level_from_user(self, message: Message):
        await self.BOT_INSTANCE.send_message(message.chat.id,
                                             f"Кажется, уровня подготовки под номером '{message.text}' не существует")

    @staticmethod
    async def _check_or_get_training_levels(training_levels: list[TrainingLevel] | None) -> list[TrainingLevel]:
        """Если training_levels это список уровней подготовки, то возвращает training_levels
        без изменений, иначе возвращает список уровней подготовки."""
        if not training_levels:
            return await get_training_levels()
        return training_levels

    async def _set_selected_training_level(self, user_id: int, training_level: TrainingLevel):
        """Сохраняет выбранный пользователем уровень подготовки во временном хранилище"""
        old_user_data = await self.get_user_data(user_id)
        new_user_data = old_user_data['selected_training_level'] = training_level
        await self.set_new_user_data(user_id, new_user_data)

    async def _get_selected_training_level(self, user_id: int):
        """Получаем выбранный уровень подготовки пользователя из временного хранилище"""
        try:
            data = await self.get_user_data(user_id)
            return data['selected_training_level']
        except KeyError:
            return

    async def exit_subprogram(self, message: Message, training_levels: Optional[list[TrainingLevel]] = None):
        """Сохраняет выбранный уровень подготовки во временном хранилище, а также запускает
        подпрограмму TimezoneSubprogram"""
        training_levels = await self._check_or_get_training_levels(training_levels)
        await self._set_selected_training_level(message.chat.id, training_levels)
        await TimezoneSubprogram(self.BOT_INSTANCE).ask(message)


class TimezoneSubprogram(BaseJoinSubprogram):
    """
    Используется для получения часового пояса от пользователя.
    Данные о выбранном пользователем часовом поясе сохраняются
    во временном хранилище.
    """

    async def ask(self, message: Message):
        await self.timezone_request(message)

    async def timezone_request(self, message: Message):
        current_state = await self.BOT_INSTANCE.get_state(
            user_id=message.chat.id)  # пометка: get_state всегда возвращает строку.

        if current_state == 'JoiningStates:timezone_request':
            await self.BOT_INSTANCE.send_message(chat_id=message.chat.id, text='Кажется, что-то пошло не так')
        else:
            await self.STATE_CONTROLLER.set_timezone_request(message.chat.id)

        rendered_text = render_template(template_name='timezone_request')

        await self.BOT_INSTANCE.send_message(
            chat_id=message.chat.id,
            text=rendered_text,
            reply_markup=keyboards.delete_keyboad()
        )

    async def timezone_preview(self, message: Message):
        await self.STATE_CONTROLLER.set_timezone_preview(message.chat.id)

        message_text = message.text
        datetime_text = get_datetime_text(message_text)

        rendered_text = render_template(
            'timezone_preview',
            {
                'user_timezone': message_text,
                'user_datetime': datetime_text
            }
        )

        await self.BOT_INSTANCE.send_message(
            chat_id=message.chat.id,
            text=rendered_text,
            reply_markup=keyboards.get_yes_or_no_keyboard()
        )

        await self._set_selected_timezone(message.chat.id, int(message_text))

    async def _set_selected_timezone(self, user_id: int, timezone_value: int):
        old_user_data = await self.get_user_data(user_id)
        new_user_data = old_user_data['selected_timezone'] = timezone_value
        await self.set_new_user_data(user_id, new_user_data)

    async def exit_subprogram(self, message: Message):
        """Запускаем процесс формирования заявки на вступление и очищаем временное хранилище"""

        await self.set_new_user_data(message.chat.id, {})


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
    """Формат вывода:
    2023-10-27 12:51:56.731499+09:00"""
    if is_russian_utc(value):
        desired_timezone = pytz.FixedOffset(int(value) * 60)
        current_time = datetime.now(desired_timezone)
        return current_time
    return None


def get_datetime_text(timezone_value: str | int) -> str:
    """Формат вывода:
    12:50. Октябрь, 20 число"""
    datetime_value = _get_full_datetime_with_timezone(timezone_value)
    time = datetime_value.time().strftime("%H:%M")
    date = datetime_value.date().strftime("%d %m")
    day, month_digit = date.split(' ')
    month_text = _convert_digit_to_month(month_digit)
    datetime_text = f"{time}. {_to_upper_first_letter(month_text)}, {day} число"
    return datetime_text


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


def _to_upper_first_letter(text: str) -> str:
    try:
        return text[0].upper() + text[1::]
    except IndexError:
        return text


async def register_handlers(bot):
    training_level_handler = TrainingLevelSubprogram(bot)
    timezone_handler = TimezoneSubprogram(bot)
    training_levels = await get_training_levels()

    @bot.message_handler(state=JoiningStates.training_level_request, is_digit=False)
    async def incorrect_number(new_message: Message):
        """
        Выполняется, если пользователь ввёл строку
        """
        await training_level_handler.incorrect_get_training_level_from_user(new_message)

    """Хендлены, относящиеся к TrainingLevelSubprogram"""

    @bot.message_handler(state=JoiningStates.training_level_request, is_digit=True)
    async def correct_number(new_message: Message):
        """
        Выполняется, если пользователь ввёл нужное число
        0 < "число, введённое пользователем" <= count_of_training_levels
        """
        if 0 < int(new_message.text) <= len(training_levels):
            await training_level_handler.training_level_preview(new_message, training_levels)
        else:
            await training_level_handler.incorrect_get_training_level_from_user(new_message)

    @bot.message_handler(state=JoiningStates.training_level_preview, text=TextFilter(equals='Нет'))
    async def disagree(new_message: Message):
        await training_level_handler.training_level_request(new_message, training_levels)

    @bot.message_handler(state=JoiningStates.training_level_preview, text=TextFilter(equals='Да'))
    async def agree(new_message: Message):
        await training_level_handler.exit_subprogram(new_message, training_levels)

    @bot.message_handler(state=JoiningStates.training_level_preview, content_types=['text'])
    async def other_text(new_message: Message):
        await bot.send_message(
            chat_id=new_message.chat.id,
            text="Выберите один из предложенных вариантов, пожалуйста",
            reply_markup=keyboards.get_yes_or_no_keyboard()
        )

    """Хендлены, относящиеся к TimezoneSubprogram"""

    @bot.message_handler(state=JoiningStates.timezone_request, is_digit=False)
    async def incorrect_number(new_message: Message):
        await timezone_handler.timezone_request(new_message)

    @bot.message_handler(state=JoiningStates.timezone_request, is_digit=True)
    async def correct_number(new_message: Message):
        if is_russian_utc(new_message.text):
            await timezone_handler.timezone_preview(new_message)
        else:
            await timezone_handler.timezone_request(new_message)

    @bot.message_handler(state=JoiningStates.timezone_preview, text=TextFilter(equals='Да'))
    async def agree(new_message: Message):
        await timezone_handler.exit_subprogram(new_message)

    @bot.message_handler(state=JoiningStates.timezone_preview, text=TextFilter(equals='Нет'))
    async def disagree(new_message: Message):
        await timezone_handler.timezone_request(new_message)

    @bot.message_handler(state=JoiningStates.timezone_preview, content_types=['text'])
    async def other_text(new_message: Message):
        await bot.send_message(
            chat_id=new_message.chat.id,
            text="Выберите один из предложенных вариантов, пожалуйста",
            reply_markup=keyboards.get_yes_or_no_keyboard()
        )


if __name__ == '__main__':
    pass
