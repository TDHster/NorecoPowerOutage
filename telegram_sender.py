# telegram_sender.py
import asyncio
from pathlib import Path
from typing import List, Union
from aiogram import Bot
from aiogram.types import FSInputFile
from config import Settings
from logger import logger

settings = Settings()

async def send_images_to_group(image_paths: List[Union[str, Path]]) -> None:
    """Send list of images to Telegram group"""
    bot = Bot(token=settings.TELEGRAM_BOT_API)
    
    try:
        for image_path in image_paths:
            path = Path(image_path)
            if path.exists() and path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                logger.debug(f'Sending to group file {path}')
                photo = FSInputFile(path)
                await bot.send_photo(chat_id=settings.TELEGRAM_GROUP_ID, photo=photo)
    finally:
        await bot.session.close()