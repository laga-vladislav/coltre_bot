from typing import Optional, TypeAlias
from telebot.types import ReplyKeyboardMarkup

from coltre_bot.exceptions import WrongDataNumbersKeyboard

NumbersList: TypeAlias = list[int]
LenOfRange: TypeAlias = int

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
    markup = ReplyKeyboardMarkup(row_width=row_width, one_time_keyboard=one_time)
    print(buttons)
    markup.add(*[button for button in buttons])
    return markup


if __name__ == '__main__':
    print(get_numbers_keyboard(data=3, row_width=11, one_time=False))
