# save_images_from_links.py

import time
import random
import requests
from pathlib import Path
from urllib.parse import urlparse

from logger import logger

def save_images(urls: list[str], save_dir: Path = Path("images")) -> list[Path]:
    save_dir.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for i, url in enumerate(urls, 1):
        try:
            filename = Path(urlparse(url).path).name
            filepath = save_dir / filename

            if filepath.exists():
                logger.debug(f"{i:02d}. ⏭️ Уже скачано: {filename}")
                continue

            logger.debug(f"{i:02d}. ⬇️ Скачиваю: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            filepath.write_bytes(response.content)
            saved_files.append(filepath)  # добавляем только что сохранённый файл
            logger.info(f"    ✅ Сохранено: {filepath}")

            time.sleep(random.uniform(2, 4))  # Антибот-таймер

        except requests.exceptions.RequestException as e:
            logger.error(f"{i:02d}. ❌ network error {url}: {e}")
        except Exception as e:
            logger.error(f"{i:02d}. ❌ Unknown error: {e}")

    return saved_files



if __name__ == "__main__":
    links = [        
        "https://static.wixstatic.com/media/2c4ad4_bccbf1f594b44d9484d912309625039b~mv2.jpg",
        "https://static.wixstatic.com/media/2c4ad4_c24606f017bd405e8152605ddd9bef59~mv2.jpg",
        "https://static.wixstatic.com/media/2c4ad4_cf5bbc3a7900420bbc91634a1055b211~mv2.jpg"
    ]
    save_images(links)
