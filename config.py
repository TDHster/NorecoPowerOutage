# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_API: str
    TELEGRAM_GROUP_ID: str
    LOG_LEVEL: str = "INFO"  
    MEDIA_FILE_ON_SITE_PATTERN: str
    URL: str
    IMAGES_DIR: str = "images"

    class Config:
        env_file = ".env"   # сначала ищет в env, потом в .env
        env_file_encoding = "utf-8"

# Создаём один общий экземпляр, который можно импортировать везде
config = Settings()

#Example usage:
# from config import config
# print(config.LOG_LEVEL)  # beware intellisence hint not work, because names are dynamic