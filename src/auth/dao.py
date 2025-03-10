from logging import Logger, getLogger
import asyncio
from typing import Any, Sequence
from fastapi import HTTPException, Depends
from sqlalchemy import Table, text
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import TextClause

from pydantic import BaseModel

from src.core.base_dao import BaseDao
from src.core.models import user_table

logger: Logger = getLogger(__name__)


class AuthDao(BaseDao):
    model: Table = user_table

    async def add(self, model: BaseModel) -> None:
        model_dict: dict = model.model_dump()

        logger.info("Будем добавлять  %s", model_dict)
        try:
            stmt: TextClause = text(
                f"INSERT INTO {self.model.name} (name, email, password, roles_id) \
                                     VALUES (:name, :email, :password, :roles_id)"
            )
            stmt = stmt.bindparams(**model_dict)

            await self._session.execute(stmt)
        except SQLAlchemyError as e:
            logger.error("Ошибка %s", e)
            raise HTTPException(
                status_code=500, detail=f"При обработке вашего запроса произошла ошибка"
            )

    async def get_roles_user(self, user_id: int) -> str | None:
        try:
            query: TextClause = text(
                "SELECT roles.name FROM roles JOIN users ON roles.id = users.roles_id \
                                     WHERE users.id = :user_id"
            )
            query = query.bindparams(user_id=user_id)
            result = await self._session.execute(query)
            res: str | None = result.scalar_one_or_none()
            return res
        except SQLAlchemyError as e:
            logger.error("Ошибка %s", e)
            raise HTTPException(
                status_code=500, detail="При обработке вашего запроса произошла ошибка"
            )
        
    async def find_all(self) -> Sequence[Row[Any]] | None:
        try:
            query: TextClause = text("SELECT users.id, users.name, email, roles.name FROM users \
                                     JOIN roles ON roles_id = roles.id")
            result = await self._session.execute(query)
            res: Sequence[Row[Any]] = result.fetchall()
            logger.info("Найдены записи %s", res)
            return res
        except SQLAlchemyError as e:
            logger.error("Ошибка %s", e)


if __name__ == "__main__":
    from src.core.db_helper import db_helper

    async def main():
        async with db_helper.engine.connect() as session:
            dao = AuthDao(session)
            result: Sequence[Row[Any]] | None = await dao.find_all()
            print(f"{result=}")
        return result

    asyncio.run(main())
