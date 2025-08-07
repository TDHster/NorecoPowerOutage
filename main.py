# run_extract_and_download.py
import asyncio
from save_images_from_links import save_images_from_links  # твой модуль скачки
from wix_parser import extract_from_page                # этот модуль

async def main():
    url = "https://www.noreco2.com.ph/power-outage"
    links = await extract_from_page(url)
    save_images_from_links(links)

if __name__ == "__main__":
    asyncio.run(main())
