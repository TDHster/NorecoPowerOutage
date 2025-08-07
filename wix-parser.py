# extract_all_wix_jpgs.py
import asyncio
import re
from playwright.async_api import async_playwright
from urllib.parse import unquote


def extract_wix_jpgs_from_html(html: str) -> list[str]:
    """
    Ищет все JPG-ссылки на wixstatic.com/media/ в тексте HTML.
    """
    html = unquote(html)
    pattern = r"https://static\.wixstatic\.com/media/[^\"\'\s>\\]+?\.jpg"
    matches = re.findall(pattern, html, flags=re.IGNORECASE)
    return sorted(set(matches))


async def extract_from_page(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        html = await page.content()
        jpg_links = extract_wix_jpgs_from_html(html)

        print(f"\n🔍 Найдено {len(jpg_links)} JPG-ссылок на wixstatic.com/media/:\n")
        for i, link in enumerate(jpg_links, 1):
            print(f"{i:02d}: {link}")

        await browser.close()


if __name__ == "__main__":
    url = "https://www.noreco2.com.ph/power-outage"  # 👈 замени на свою страницу
    asyncio.run(extract_from_page(url))
