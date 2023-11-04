import asyncio
import dataclasses
from datetime import datetime
from typing import Optional

from aiomysql import IntegrityError

from coltre_bot.core.db import fetch_all, insert_data, delete_data
from coltre_bot import exceptions


@dataclasses.dataclass
class MembershipRequest:
    user_id: int
    request_date: datetime


async def request_exists(data: int | MembershipRequest) -> bool:
    result = await fetch_all(_get_request_sql_query(data if isinstance(data, int) else data.user_id))
    return len(result) > 0


class RequestValidators:
    @staticmethod
    def is_request_exists(func):
        """Декоратор. Выполняется, если заявка существует"""

        async def wrapper(data: int | MembershipRequest):
            if not await request_exists(data):
                return
            await func(data)

        return wrapper

    @staticmethod
    def is_not_request_exists(func):
        """Декоратор. Выполняется, если заявка не существует"""

        async def wrapper(data: int | MembershipRequest):
            if await request_exists(data):
                return
            await func(data)

        return wrapper


@RequestValidators.is_request_exists
async def get_request(user_id: int) -> MembershipRequest:
    get_request_sql_query = _get_request_sql_query(user_id)
    result = await fetch_all(get_request_sql_query)
    return _parse_fetch_all(result[0])


def _get_request_sql_query(user_id: int) -> str:
    """Формирует SQL-скрипт на получение заявки"""
    sql_query = f"SELECT user_id, request_date FROM membership_request WHERE user_id={user_id};"
    return sql_query


def _parse_fetch_all(membership_request: tuple) -> MembershipRequest:
    return MembershipRequest(
        user_id=membership_request[0],
        request_date=membership_request[1]
    )


@RequestValidators.is_not_request_exists
async def open_request(user_id: int):
    try:
        create_request_insert_query = _create_request_insert_sql_query(user_id)
        await insert_data(create_request_insert_query)
    except IntegrityError:
        raise exceptions.UserDoesntExist(f"Пользователя с id={user_id} не существует")


def _create_request_insert_sql_query(user_id: int) -> str:
    sql_query = f"INSERT INTO membership_request (user_id) VALUES ({user_id});"
    return sql_query


@RequestValidators.is_request_exists
async def close_request(request: MembershipRequest):
    sql_query = _delete_request_sql_query(request)
    await delete_data(sql_query)


def _delete_request_sql_query(request: MembershipRequest):
    sql_query = f"DELETE FROM membership_request WHERE user_id={request.user_id} AND request_date='{request.request_date}';"
    return sql_query


async def main():
    print(await get_request(1))
    await open_request(1)
    print(await get_request(1))

    await close_request(MembershipRequest(1, datetime(year=2023, month=11, day=2).date()))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
