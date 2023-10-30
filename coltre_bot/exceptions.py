class WrongDataNumbersKeyboard(Exception):
    """Неверный тип данных при попытке сгенерировать численную клавиатуру."""
    pass

class WrongMonthDigit(Exception):
    """Неверное число для определения месяца"""
    pass

class UserAlreadyRegistered(Exception):
    """Пользователь уже есть в базе данных"""
    pass
