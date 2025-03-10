from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    # db config
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    echo: bool = True
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")

    # auth
    private_key_path: Path = BASE_DIR / "cert" / "private.pem"  
    public_key_path: Path = BASE_DIR / "cert" / "public.pem" 
    algorithms: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

settings = Settings()
