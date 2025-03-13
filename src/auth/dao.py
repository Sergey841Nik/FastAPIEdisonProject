from logging import Logger, getLogger
import asyncio
from typing import Any, Sequence

from fastapi import HTTPException

from sqlalchemy import Table, text
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.elements import TextClause


from src.core.base_dao import BaseDao
from src.core.models import user_table, roles_table
from src.auth.schemas import UserAddDB, UserUpdateInfo
from src.exceptions import valid_integer, valid_string

logger: Logger = getLogger(__name__)

class RolesDao(BaseDao):
    model: Table = roles_table

    async def add(self, name_roles: str) -> None:
        valid_string(name_roles)
        logger.info("Будем добавлять  %s", name_roles)
        try:
            stmt: TextClause = text(
                f"INSERT INTO {self.model.name} (name) VALUES (:name)"
            )
            stmt = stmt.bindparams(name=name_roles)

            await self._session.execute(stmt)
        except SQLAlchemyError as e:
            logger.error("Ошибка %s", e)
            raise HTTPException(
                status_code=500, detail="При обработке вашего запроса произошла ошибка"
            )

    async def delete(self, id_roles: int) -> None:
        valid_integer(id_roles)
        logger.info("Будем удалять  %s", id_roles)
        try:
            query: TextClause = text(f"DELETE FROM {self.model.name} WHERE id = :id_roles")
            query = query.bindparams(id_roles=id_roles)
            await self._session.execute(query)
        except SQLAlchemyError as e:
            logger.error("Ошибка %s", e)
            

class AuthDao(BaseDao):
    model: Table = user_table

    async def add(self, model: UserAddDB) -> None:
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
                status_code=500, detail="При обработке вашего запроса произошла ошибка"
            )

    async def get_roles_user(self, user_id: int) -> str | None:
        valid_integer(user_id)
        logger.info("Будем получать роли пользователя %s", user_id)
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
            query: TextClause = text(
                "SELECT users.id, users.name, email, roles.name FROM users \
                                     JOIN roles ON roles_id = roles.id"
            )
            result = await self._session.execute(query)
            res: Sequence[Row[Any]] = result.fetchall()
            logger.info("Найдены записи %s", res)
            return res
        except SQLAlchemyError as e:
            logger.error("Ошибка %s", e)

    async def update(self, model: UserUpdateInfo) -> None:
        model_dict: dict = model.model_dump()
        logger.info("Будем обновлять записи %s", model_dict)
        try:
            stmt: TextClause = text(
                """UPDATE users SET 
                            email = COALESCE(:new_email, email), 
                            name = COALESCE(:new_name, name)
                    WHERE id = :user_id"""
            )
            stmt = stmt.bindparams(**model_dict)
            await self._session.execute(stmt)
        except SQLAlchemyError as e:
            logger.error("Ошибка %s", e)
            raise HTTPException(
                status_code=500, detail="При обработке вашего запроса произошла ошибка"
            )
        await self._session.execute(stmt)


if __name__ == "__main__":
    from src.core.db_helper import db_helper

    async def main():
        async with db_helper.engine.connect() as session:
            dao = AuthDao(session)
            result: Sequence[Row[Any]] | None = await dao.find_all()
            print(f"{result=}")
        return result

    asyncio.run(main())
