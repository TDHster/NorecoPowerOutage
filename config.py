# config.py

from pydantic import BaseSettings

class Settings(BaseSettings):

    class Config:
        env_file = ".env"  # если файл есть — берёт оттуда, если нет — игнорирует

#Example usage:
# from config import config
# print(config.LOG_LEVEL)  # beware intellisence hint not work, because names are dynamic