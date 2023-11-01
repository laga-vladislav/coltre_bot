import asyncio
import dataclasses

from typing import Optional

from coltre_bot.core.db import fetch_all, insert_data
from coltre_bot.exceptions import UserAlreadyRegistered


@dataclasses.dataclass
class User:
    def __init__(
            self,
            user_id: int,
            first_name: str,
            training_level_id: int,
            timezone: int,
            group_id: Optional[int] = None,
            username: Optional[str] = None,
    ):
        if not (all([user_id, first_name, training_level_id, timezone])):
            raise ValueError("user_id, first_name, group_id cannot be None")
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.training_level_id = training_level_id
        self.group_id = group_id
        self.timezone = timezone


async def is_registered(user_id: int) -> bool:
    """
    Проверка на то, зарегистрирован ли пользователь
    """
    if await get_user_by_id(user_id) is not None:
        return True
    return False


async def register_user(user_instance: User) -> None:
    """
    Регистрация пользователя в базе данных
    """
    if not await is_registered(user_id=user_instance.user_id):
        register_user_sql_query = _register_user_sql_query(user_instance)
        await insert_data(register_user_sql_query)
    else:
        raise UserAlreadyRegistered('Пользователь уже зарегистрирован')



def _register_user_sql_query(user_instance: User):
    """
    Формирует SQL-скрипт на регистрацию пользователя
    """
    params = user_instance.__dict__
    valid_keys = [key for key in params.keys() if params[key] is not None]
    keys_str = ', '.join(valid_keys)
    valid_values = [params[key] for key in valid_keys]
    values_str = ', '.join([f'{val!r}' if not isinstance(val, (int, float)) else str(val) for val in valid_values])
    sql_query = \
        f"INSERT INTO user ({keys_str}) VALUES ({values_str});"
    return sql_query


async def get_user_by_id(user_id: int) -> User | None:
    """
    Получить объект User, используя его айди
    """
    get_user_sql_query = _get_user_sql_query(user_id)
    results = await fetch_all(get_user_sql_query)
    if len(results) > 0:
        user = _parse_fetch_all(results[0])
        return user
    return None


async def is_group_member(user_or_user_id: int | User):
    user = user_or_user_id
    if isinstance(user_or_user_id, int):
        user = await get_user_by_id(user)
    if user.group_id:
        return True
    return False


def _get_user_sql_query(user_id: int):
    """
    Формирует SQL-скрипт на получение пользователя по его айди
    """
    return f"""SELECT * FROM user WHERE user_id = {user_id};"""


def _parse_fetch_all(results: tuple) -> User:
    return User(
        user_id=results[0],
        username=results[1],
        first_name=results[2],
        training_level_id=results[3],
        group_id=results[4],
        timezone=results[5]
    )


async def main():
    user = User(
        user_id=2,
        first_name='ksdljfklsdajfklasjd;fasdf',
        training_level_id=2,
        timezone=4
    )
    ff = await is_group_member(user)
    print(ff)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
