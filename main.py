# main.py
import asyncio
from save_images_from_links import save_images  
from wix_parser import extract_from_page                
from telegram_sender import send_images_to_group
from pathlib import Path
from logger import logger
from config import config
from remove_nonlist_file import delete_unlisted
from urllib.parse import urlparse
from pathlib import Path

async def main():
    url = config.URL

    logger.info("Scraping links...")
    links = await extract_from_page(url)

    logger.info(f"Saving {len(links)} ...")
    new_images_names = save_images(links)
    logger.info(f'Found {len(new_images_names)} new images.')

    all_filenames_from_urls = [Path(urlparse(u).path).name for u in links]
    delete_unlisted(all_filenames_from_urls)
    
    logger.info("Sending to Telegram...")
    await send_images_to_group(new_images_names)

if __name__ == "__main__":
    asyncio.run(main())