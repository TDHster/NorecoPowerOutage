# main.py
import asyncio
from save_images_from_links import save_images  
from wix_parser import extract_from_page                
from easyocr import recognize_text_in_folder                  
from telegram_sender import send_images_to_group
from pathlib import Path
from logger import logger
from config import config

async def main():
    # url = "https://www.noreco2.com.ph/power-outage"
    url = config.URL

    logger.info("Scraping links...")
    links = await extract_from_page(url)

    logger.info(f"Saving {len(links)} ...")
    paths = save_images(links)
    logger.info(f'Founded {len(paths)} new images.')
    # logger.info("🔎 Запускаем распознавание текста...")
    # recognize_text_in_folder(Path("images"))
    
    logger.info("Sending to Telegram...")
    await send_images_to_group(paths)

if __name__ == "__main__":
    asyncio.run(main())
