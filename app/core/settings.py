from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import BaseModel


root_dir = Path(__file__).parent.parent


class _Path(BaseModel):
    root_dir: Path = root_dir


class YandexAPI(BaseModel):
    client_login: str
    client_id: str
    client_secret: str


class _Settings(BaseSettings):

    yandex: YandexAPI
    domain: str

    app_path: _Path = _Path()

    class Config:
        env_file = Path(root_dir, 'config', 'dev.ini')
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '.'


Settings = _Settings()
