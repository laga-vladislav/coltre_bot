from typing import Optional, TypeAlias
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from coltre_bot.exceptions import WrongDataNumbersKeyboard

NumbersList: TypeAlias = list[int]
LenOfRange: TypeAlias = int

def delete_keyboad() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def get_numbers_keyboard(
        data: NumbersList | LenOfRange,
        row_width: int = 1,
        one_time: Optional[bool] = True
) -> ReplyKeyboardMarkup:
    """Используется в случаях, когда необходимо выбрать одно из чисел в известном диапазоне"""
    if type(data) == NumbersList:
        buttons = [str(number) for number in data]
    elif type(data) == LenOfRange:
        buttons = [str(number + 1) for number in range(data)]
    else:
        raise WrongDataNumbersKeyboard('Был передан неверный тип в качестве даты для генерации клавиатуры.')
    markup = ReplyKeyboardMarkup(row_width=row_width, one_time_keyboard=one_time, resize_keyboard=True)
    markup.add(*[button for button in buttons])
    return markup


def get_yes_or_no_keyboard(row_width: int = 2, one_time: Optional[bool] = True) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=row_width, one_time_keyboard=one_time, resize_keyboard=True)
    markup.add('Да', 'Нет')
    return markup


if __name__ == '__main__':
    print(get_numbers_keyboard(data=3, row_width=11, one_time=True))
    print(get_yes_or_no_keyboard())
