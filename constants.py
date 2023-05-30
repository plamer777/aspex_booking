"""This file contains constants to configure the application"""
from datetime import timedelta, timezone
from pydantic import BaseSettings
# --------------------------------------------------------------------------

ENV_FILE = '.env'


class Settings(BaseSettings):
    """This class serves to get settings from the environment variables"""
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    JWT_SECRET: str
    JWT_ALGO: str
    JWT_EXP_HOURS: int
    TZ_SHIFT: float
    API_TITLE: str
    API_DESCRIPTION: str
    API_VERSION: str

    class Config:
        env_file = ENV_FILE


sets = Settings()

README_FILE = 'README.md'

DB_URI = (f'postgresql+asyncpg://{sets.POSTGRES_USER}:{sets.POSTGRES_PASSWORD}'
          f'@{sets.POSTGRES_HOST}:{sets.POSTGRES_PORT}/{sets.POSTGRES_DB}')

JWT_SECRET = sets.JWT_SECRET
JWT_ALGO = sets.JWT_ALGO
JWT_EXP_HOURS = sets.JWT_EXP_HOURS

TOKEN_URL = '/login'

DEADLINE_HOURS = 1
TZ = timezone(timedelta(hours=sets.TZ_SHIFT))

API_TITLE = sets.API_TITLE
API_DESCRIPTION = sets.API_DESCRIPTION
API_VERSION = sets.API_VERSION
