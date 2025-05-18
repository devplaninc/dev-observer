from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Github(BaseModel):
    auth_type: str
    personal_token: Optional[str] = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='dev_observer__',
        env_nested_delimiter='__',
    env_file=('.env', '.env.local'),
    )

    github: Optional[Github] = None

settings = Settings()
