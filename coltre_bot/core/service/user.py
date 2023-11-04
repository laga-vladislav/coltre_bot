import asyncio
import dataclasses

from typing import Optional

from coltre_bot.core.db import fetch_all, insert_data


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
            raise ValueError("user_id, first_name, training_level_id, timezone cannot be None")
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.training_level_id = training_level_id
        self.group_id = group_id
        self.timezone = timezone


def make_user_instance(user_id: int,
                       first_name: str,
                       training_level_id: int,
                       timezone: int,
                       group_id: Optional[int] = None,
                       username: Optional[str] = None) -> User:
    return User(
        user_id,
        first_name,
        training_level_id,
        timezone,
        group_id,
        username
    )


async def get_user_by_id(user_id: int) -> User | None:
    get_user_sql_query = _get_user_sql_query(user_id)
    results = await fetch_all(get_user_sql_query)
    print(results)
    if results != ():
        user = _parse_fetch_all(results[0])
        return user
    return None


class UserValidators:
    @staticmethod
    def is_registered(func) -> bool:
        """Декоратор. Выполняется, если пользователь зарегистрирован"""

        async def wrapper(data: int | User):
            if not await get_user_by_id(data if isinstance(data, int) else data.user_id):
                return
            await func(data)

        return wrapper

    @staticmethod
    def is_not_registered(func) -> bool:
        """Декоратор. Выполняется, если пользователь НЕ зарегистрирован"""

        async def wrapper(data: int | User):
            if await get_user_by_id(data if isinstance(data, int) else data.user_id):
                return
            await func(data)

        return wrapper


@UserValidators.is_not_registered
async def register_user(user_instance: User) -> None:
    """Регистрация пользователя в базе данных"""
    register_user_sql_query = _register_user_sql_query(user_instance)
    await insert_data(register_user_sql_query)


def _register_user_sql_query(user_instance: User):
    """Формирует SQL-скрипт на регистрацию пользователя"""
    params = user_instance.__dict__
    valid_keys = [key for key in params.keys() if params[key] is not None]
    keys_str = ', '.join(valid_keys)
    valid_values = [params[key] for key in valid_keys]
    values_str = ', '.join([f'{val!r}' if not isinstance(val, (int, float)) else str(val) for val in valid_values])
    sql_query = \
        f"INSERT INTO user ({keys_str}) VALUES ({values_str});"
    return sql_query


@UserValidators.is_registered
async def is_group_member(data: int | User):
    user = data
    if isinstance(data, int):
        user = await get_user_by_id(user)
    if user.group_id:
        return True
    return False


def _get_user_sql_query(user_id: int):
    """Формирует SQL-скрипт на получение пользователя по его айди"""
    return f"""SELECT * FROM user WHERE user_id = {user_id};"""


def _parse_fetch_all(result: tuple) -> User:
    return User(
        user_id=result[0],
        username=result[1],
        first_name=result[2],
        training_level_id=result[3],
        group_id=result[4],
        timezone=result[5]
    )


async def main():
    user = User(
        user_id=2,
        first_name='ksdljfklsdajfklasjd;fasdf',
        training_level_id=2,
        timezone=4
    )
    print(make_user_instance(1, '2', 3, 4).__dict__)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
