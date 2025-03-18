from pathlib import Path
from contextlib import nullcontext
from typing import Any, Sequence

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy.engine.row import Row

from src.auth.schemas import UserAddDB, UserUpdateInfo
from src.auth.dao import AuthDao, RolesDao
from src.core.config import settings
from src.core.models import metadata
from src.core.db_helper import DBHelper

BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "tests" / "test_db.db"
url: str = f"sqlite+aiosqlite:///{DB_PATH}"
db_helper = DBHelper(url)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_engine() -> None:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)

    async with db_helper.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@pytest.mark.asyncio
async def test_add_roles() -> None:
    async with db_helper.engine.connect() as session:
        dao = RolesDao(session)
        await dao.add("user")
        await dao.add("admin")
        await session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, expectation",
    (
        (
            {"name": "test1", "email": "test1@test.com", "password": "test"},
            nullcontext(),
        ),
        (
            {"name": "test2", "email": "test2@test.com", "password": "test"},
            nullcontext(),
        ),
        (
            {
                "name": "test3",
                "email": "test3@test.com",
                "password": "test",
                "roles_id": 2,
            },
            nullcontext(),
        ),
        (
            {"name": "test4", "email": "test4test.com", "password": "test"},
            pytest.raises(ValidationError),
        ),
    ),
)
async def test_add_users(user_data, expectation) -> None:
    with expectation:
        user = UserAddDB(**user_data)

    async with db_helper.engine.connect() as session:
        dao = AuthDao(session)
        if isinstance(expectation, nullcontext):
            await dao.add(user)
            await session.commit()


@pytest.mark.asyncio
async def test_get_roles_user() -> None:
    async with db_helper.engine.connect() as session:
        dao = AuthDao(session)
        assert await dao.get_roles_user(1) == "user"
        assert await dao.get_roles_user(3) == "admin"
        assert await dao.get_roles_user(4) is None


@pytest.mark.asyncio
async def test_find_all() -> None:
    async with db_helper.engine.connect() as session:
        dao = AuthDao(session)
        result: Sequence[Row[Any]] | None = await dao.find_all()
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0][0] == 1
        assert result[1][1] == "test2"
        assert result[2][2] == "test3@test.com"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expectation",
    (
        (1, nullcontext()),
        (2, nullcontext()),
        (3, nullcontext()),
        ("4", pytest.raises(TypeError, match="Значение должно быть целым числом")),
    ),
)
async def test_find_one_or_none_by_id(user_id, expectation) -> None:
    async with db_helper.engine.connect() as session:
        dao = AuthDao(session)
        with expectation:
            result: Sequence[Row[Any]] = await dao.find_one_or_none_by_id(user_id)
            assert isinstance(result, Row)
            assert not isinstance(result, tuple)
            assert result[0] == user_id
            assert result[1] == f"test{user_id}"
            assert result[2] == f"test{user_id}@test.com"

        assert await dao.find_one_or_none_by_id(4) is None

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, expectation",
    (
        ("test1@test.com", nullcontext()),
        ("test2@test.com", nullcontext()),
        ("test3@test.com", nullcontext()),
        (4, pytest.raises(TypeError, match="Значение должно быть строкой")),
    ),
)
async def test_find_one_or_none(email, expectation):
    async with db_helper.engine.connect() as session:
        dao = AuthDao(session)
        with expectation:          
            result: Sequence[Row[Any]] = await dao.find_one_or_none(email)
            assert isinstance(result, Row)
            assert not isinstance(result, tuple)
            assert result[2] == email

        assert await dao.find_one_or_none("test") is None #Просто строка тоже не выдаёт ошибок, надо поправить

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_update_data, expectation",
    (
        ({"user_id": 1, "new_name": "new_test1"}, nullcontext()),
        ({"user_id": 2, "new_email": "new_test2@test.com"}, nullcontext()),
        (
            {"user_id": 3, "new_name": "new_test3", "new_email": "new_test3@test.com"},
            nullcontext(),
        ),
        (
            {"user_id": 1, "new_name": "test4", "new_email": "test1test.com"},
            pytest.raises(ValidationError),
        ),
    ),
)
async def test_update(user_update_data, expectation) -> None:
    with expectation:
        user_update = UserUpdateInfo(**user_update_data)
    async with db_helper.engine.connect() as session:
        dao = AuthDao(session)
        if isinstance(expectation, nullcontext):
            await dao.update(user_update)
            await session.commit()
            user_id = user_update.user_id
            result: Sequence[Row[Any]] = await dao.find_one_or_none_by_id(user_id)

            assert result[0] == user_id

            if user_update.new_name:
                assert result[1] == user_update.new_name
            if user_update.new_email:
                assert result[2] == user_update.new_email
