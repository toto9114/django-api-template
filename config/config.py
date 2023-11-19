from typing import Optional
from os.path import join
import environ

root = environ.Path(__file__) - 2  # get root of the project
env = environ.Env()
environ.Env.read_env(join(root, ".env"))  # reading .env file

APP_NAME: str = env.str("APP_NAME", "django-api-template")
DEBUG: bool = env.bool("DEBUG", True)

# Django Secret Key
SECRET_KEY: str = env.str(
    "SECRET_KEY", "*dlh7&al(aip7(%j@wqjk+!05gd7d&_ed1v1@6$)2o!*20bzev"
)

# logger
LOG_DIR: str = env.str("LOG_DIR", "./logs")
LOG_LEVEL: str = env.str("LOG_LEVEL", "INFO")
LOG_HOST: Optional[str] = env.str("LOG_HOST", None)
LOG_PORT: int = env.int("LOG_PORT", 10518)

# DB
# MYSQL_HOST: str = env.str("MYSQL_HOST")
# MYSQL_PORT: int = env.int("MYSQL_PORT", 3306)
# MYSQL_USER: str = env.str("MYSQL_USER")
# MYSQL_DB: str = env.str("MYSQL_DB")
# MYSQL_PASSWORD: str = env.str("MYSQL_PASSWORD")
# MYSQL_POOL_SIZE: int = env.int("MYSQL_POOL_SIZE", 3)
# MYSQL_CONNECTION_TIMEOUT: int = env.int("MYSQL_CONNECTION_TIMEOUT", 20)

# Auth
ACCESS_TOKEN_LIFETIME: int = env.int("ACCESS_TOKEN_LIFETIME", 60 * 60)
REFRESH_TOKEN_LIFETIME: int = env.int("REFRESH_TOKEN_LIFETIME", 24 * 60 * 60)
