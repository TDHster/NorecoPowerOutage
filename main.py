# main.py
import asyncio
from save_images_from_links import save_images  
from wix_parser import extract_from_page                
# from ocr import recognize_text_in_folder                  
from pathlib import Path


async def main():
    url = "https://www.noreco2.com.ph/power-outage"

    print("🌐 Извлекаем ссылки с сайта...")
    links = await extract_from_page(url)

    print(f"📥 Сохраняем {len(links)} изображений...")
    save_images(links)

    print("🔎 Запускаем распознавание текста...")
    recognize_text_in_folder(Path("images"))

if __name__ == "__main__":
    asyncio.run(main())
