import pytest
import pytest_asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.core.models import metadata
from src.auth.dao import RolesDao
from src.core.db_helper import DBHelper, db_helper

# Тестовые данные
TEST_USER = {
    "name": "testuser",
    "email": "test@example.com",
    "password": "testpass",
    "confirm_password": "testpass",
}

# Создаем тестовый db_helper
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "tests" / "test_db.db"
url: str = f"sqlite+aiosqlite:///{DB_PATH}"
test_db_helper = DBHelper(url=url)


# Переопределяем зависимости FastAPI для тестов
async def override_get_session_with_commit():
    async with test_db_helper.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def override_get_session_without_commit():
    async with test_db_helper.session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Переопределяем зависимости в приложении
app.dependency_overrides[db_helper.get_session_with_commit] = (
    override_get_session_with_commit
)
app.dependency_overrides[db_helper.get_session_without_commit] = (
    override_get_session_without_commit
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    # Удаляем все таблицы
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    # Создаем таблицы заново
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@pytest_asyncio.fixture(autouse=True)
async def clear_database():
    """Очистка БД перед каждым тестом"""
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@pytest.mark.asyncio
async def test_add_roles() -> None:
    async with test_db_helper.engine.connect() as session:
        dao = RolesDao(session)
        await dao.add("user")
        await dao.add("admin")
        await session.commit()


@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def test_user_token(async_client):
    """Фикстура для создания тестового пользователя и получения токена"""
    # Регистрация пользователя
    response = await async_client.post("/auth/register/", json=TEST_USER)
    assert response.status_code == 201

    # Логин и получение токена
    response = await async_client.post(
        "/auth/login/",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.mark.asyncio
async def test_register_user(async_client):
    """Тест регистрации пользователя"""
    # Регистрация первого пользователя
    response = await async_client.post("/auth/register/", json=TEST_USER)
    assert response.status_code == 201

    # Попытка повторной регистрации
    response = await async_client.post("/auth/register/", json=TEST_USER)
    assert response.status_code == 409

    # Регистрация нового пользователя
    new_user = TEST_USER.copy()
    new_user["email"] = "new_test@example.com"
    response = await async_client.post("/auth/register/", json=new_user)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_login(async_client):
    """Тест входа в систему"""
    # Регистрация пользователя
    response = await async_client.post("/auth/register/", json=TEST_USER)
    assert response.status_code == 201

    # Успешный вход
    response = await async_client.post(
        "/auth/login/",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Неверный пароль
    response = await async_client.post(
        "/auth/login/",
        data={"username": TEST_USER["email"], "password": "wrong_password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_info(async_client, test_user_token):
    """Тест получения информации о пользователе"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await async_client.get("/auth/user/me/", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == TEST_USER["email"]
    assert user_data["name"] == TEST_USER["name"]


@pytest.mark.asyncio
async def test_update_user(async_client, test_user_token):
    """Тест обновления данных пользователя"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    update_data = {"new_name": "updated_name", "new_email": "updated@example.com"}

    # Обновление данных
    response = await async_client.put(
        "/auth/user/me/update_user/", headers=headers, json=update_data
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Данные успешно обновлены"}

    # Проверка обновленных данных
    response = await async_client.get("/auth/user/me/", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == update_data["new_email"]
    assert user_data["name"] == update_data["new_name"]


@pytest.mark.asyncio
async def test_refresh_token(async_client):
    """Тест обновления токена"""
    # Регистрация пользователя
    response = await async_client.post("/auth/register/", json=TEST_USER)
    assert response.status_code == 201

    # Получение refresh токена через логин
    response = await async_client.post(
        "/auth/login/",
        data={"username": TEST_USER["email"], "password": TEST_USER["password"]},
    )
    refresh_token = response.cookies.get("refresh_token")

    # Тест обновления токена
    response = await async_client.post(
        "/auth/refresh/", cookies={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


if __name__ == "__main__":
    pytest.main(["-v"])
