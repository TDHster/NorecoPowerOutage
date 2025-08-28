# extract_all_wix_jpgs_with_carousel_smart_stop.py
import asyncio
import re
from urllib.parse import unquote
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from logger import logger
from config import config
from random import randint

def extract_wix_jpgs_from_html(html: str) -> list[str]:
    html = unquote(html)
    # pattern = r"https://static\.wixstatic\.com/media/[^\"\'\s>\\]+?\.jpg"
    # pattern = rf"{config.MEDIA_FILE_ON_SITE_PATTERN}"
    pattern = r"https://static\.wixstatic\.com/media/[^\"\'\s>\\]+?\.jpg"
    matches = re.findall(pattern, html, flags=re.IGNORECASE)
    return sorted(set(matches))


async def click_carousel_until_end(page, max_clicks=30):
    logger.debug(f"Clicking carousel at {config.URL}")
    last_html = ""
    for i in range(max_clicks):
        button = await page.query_selector('button[data-hook="nav-arrow-next"]')
        if not button:
            logger.debug("Button 'next' not found, seems to be finish.")
            break

        is_visible = await button.is_visible()
        is_enabled = await button.is_enabled()
        if not (is_visible and is_enabled):
            logger.debug("Button 'next' not acitve, seems to be finish.")
            break

        try:
            await asyncio.sleep(randint(1, 3)) # seconds
            await button.click()
            logger.debug('"Clicking" Next button')
            await page.wait_for_timeout(600)  
            
            new_html = await page.content()
            if new_html == last_html:
                logger.debug("HTML not changed, seems to be finish.")
                break
            last_html = new_html
        except PlaywrightTimeout:
            logger.debug("Timeout while loading.")
            break


async def extract_from_page(url: str):
    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=True)
        
        browser = await p.chromium.launch(
            headless=True,
            # executable_path="/ms-playwright/chromium-1181/chrome-linux/chrome"
        )
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        await click_carousel_until_end(page)

        html = await page.content()
        image_links = extract_wix_jpgs_from_html(html)

        logger.info(f"Founded {len(image_links)} at wixstatic.com/media/:\n")
        for i, link in enumerate(image_links, 1):
            logger.debug(f"Founded at webpage: {i:02d}: {link}")

        await browser.close()
        return image_links


if __name__ == "__main__":
    url = "https://www.noreco2.com.ph/power-outage"
    asyncio.run(extract_from_page(url))
