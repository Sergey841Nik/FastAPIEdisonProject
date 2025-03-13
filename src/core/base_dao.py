from typing import Any, TypeVar, Type
from logging import Logger, getLogger

from sqlalchemy import Row, Table, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql.elements import TextClause

from src.exceptions import valid_integer, valid_string

logger: Logger = getLogger(__name__)

T = TypeVar("T", bound=Table)


class BaseDao:
    model: Type[T] = None

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def find_one_or_none_by_id(self, data: int) -> Row[Any] | None:
        valid_integer(data)
        try:
            query: TextClause = text(f"SELECT * FROM {self.model.name} WHERE id = :id")
            query = query.bindparams(id=data)
            result = await self._session.execute(query)
            rec: Row[Any] | None = result.one_or_none()
            logger.info(
                "Запись в таблице %s с ID %s %s",
                self.model.name,
                data,
                "найдена" if rec else "не найдена",
            )
            return rec
        except SQLAlchemyError as e:
            logger.error("Ошибка %s при поиске записи с %s", e, data)

    async def find_one_or_none(self, data: str) -> Row[Any] | None:
        valid_string(data)
        try:
            query: TextClause = text(
                f"SELECT * FROM {self.model.name} WHERE email = :data"
            )
            query = query.bindparams(data=data)
            result = await self._session.execute(query)
            rec: Row[Any] | None = result.one_or_none()

            logger.info(
                "Запись в таблице %s с %s %s",
                self.model.name,
                data,
                "найдена" if rec else "не найдена",
            )
            return rec
        except SQLAlchemyError as e:
            logger.error("Ошибка %s при поиске записи с %s", e, data)


if __name__ == "__main__":
    from src.core.models import user_table
    from src.core.db_helper import db_helper
    import asyncio

    class Test(BaseDao):
        model: Table = user_table

    async def main():
        async with db_helper.engine.connect() as ses:
            dao = Test(ses)

            res = await dao.find_one_or_none("serg@example.com")
            print(res)

    asyncio.run(main())
