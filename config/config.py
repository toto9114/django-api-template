import os
from os.path import join, dirname
from typing import Optional

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "./", ".env")
load_dotenv(dotenv_path)

APP_NAME: str = "django-api-template"

# logger
LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_HOST: Optional[str] = os.getenv("LOG_HOST", None)
LOG_PORT: int = int(os.getenv("LOG_PORT", 10518))

# DB
MYSQL_HOST: str = os.getenv("MYSQL_HOST")
MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER: str = os.getenv("MYSQL_USER")
MYSQL_DB: str = os.getenv("MYSQL_DB")
MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
MYSQL_POOL_SIZE: int = int(os.getenv("MYSQL_POOL_SIZE", 3))
MYSQL_CONNECTION_TIMEOUT: int = int(os.getenv("MYSQL_CONNECTION_TIMEOUT", 20))

# Django Secret Key
DJANGO_SECRET_KEY: str = os.getenv("DJANGO_SECRET_KEY")

# Auth
ACCESS_TOKEN_LIFETIME: int = int(os.getenv("ACCESS_TOKEN_LIFETIME", 60 * 60))
REFRESH_TOKEN_LIFETIME: int = int(os.getenv("REFRESH_TOKEN_LIFETIME", 24 * 60 * 60))
