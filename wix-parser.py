# extract_all_wix_jpgs_with_carousel_smart_stop.py
import asyncio
import re
from urllib.parse import unquote
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


def extract_wix_jpgs_from_html(html: str) -> list[str]:
    html = unquote(html)
    pattern = r"https://static\.wixstatic\.com/media/[^\"\'\s>\\]+?\.jpg"
    matches = re.findall(pattern, html, flags=re.IGNORECASE)
    return sorted(set(matches))


async def click_carousel_until_end(page, max_clicks=30):
    print("\n🔄 Прокручиваем карусель…")
    last_html = ""
    for i in range(max_clicks):
        button = await page.query_selector('button[data-hook="nav-arrow-next"]')
        if not button:
            print("⛔ Кнопка 'вперёд' не найдена.")
            break

        is_visible = await button.is_visible()
        is_enabled = await button.is_enabled()
        if not (is_visible and is_enabled):
            print("✅ Кнопка больше неактивна — достигнут конец карусели.")
            break

        try:
            await button.click()
            await page.wait_for_timeout(600)  # дать время на загрузку

            new_html = await page.content()
            if new_html == last_html:
                print("🟡 HTML больше не меняется — возможно, всё загружено.")
                break
            last_html = new_html
        except PlaywrightTimeout:
            print("⚠️ Таймаут при ожидании загрузки.")
            break


async def extract_from_page(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        await click_carousel_until_end(page)

        html = await page.content()
        jpg_links = extract_wix_jpgs_from_html(html)

        print(f"\n🖼️ Найдено {len(jpg_links)} JPG-ссылок на wixstatic.com/media/:\n")
        for i, link in enumerate(jpg_links, 1):
            print(f"{i:02d}: {link}")

        await browser.close()


if __name__ == "__main__":
    url = "https://www.noreco2.com.ph/power-outage"
    asyncio.run(extract_from_page(url))
