class WrongDataNumbersKeyboard(Exception):
    """Неверный тип данных при попытке сгенерировать численную клавиатуру."""
    pass

class WrongMonthDigit(Exception):
    """Неверное число для определения месяца"""
    pass

# class UserAlreadyRegistered(Exception):
#     """Пользователь уже есть в базе данных"""
#     pass

class UserDoesntExist(Exception):
    """Заявка на вступление с таким айди не может быть создана, так как пользователя
     с таким id не существует"""
    pass
