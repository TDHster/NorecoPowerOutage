# Noreco Power Outage Monitor

System for monitoring power outage announcements from the Noreco website, extracting data, and notifying via Telegram.

## 🏗 Architecture & Logic Flow

The system operates as a scheduled task (Cron) within a Docker container.

1.  **Trigger**: `cron` (defined in `app-cron`) executes `run_script.sh`.
2.  **Scraping**: `main.py` calls `wix_parser.py` which uses **Playwright** to extract image links from the Noreco Wix-based site.
3.  **Processing**:
    *   `save_images_from_links.py`: Downloads new images to the `images/` directory.
    *   `remove_nonlist_file.py`: Deletes local files that are no longer present on the website to keep the storage clean.
4.  **Notification**: `telegram_sender.py` uses **aiogram** to send the downloaded images to a specific Telegram group.

## 📁 File Map

*   `main.py`: Entry point for the business logic.
*   `wix_parser.py`: Scraper using Playwright (Chromium).
*   `telegram_sender.py`: Telegram Bot API integration.
*   `config.py`: Configuration management using `pydantic-settings`.
*   `save_images_from_links.py`: Image download utility.
*   `remove_nonlist_file.py`: Cleanup utility.
*   `logger.py`: Standardized logging configuration.
*   `ocr.py` / `paddlerocr.py`: OCR modules (currently optional/commented out in main).

## 🚀 Infrastructure & Deployment

*   **Docker**: Managed via `docker-compose.yml`.
*   **Base Image**: `mcr.microsoft.com/playwright/python:v1.54.0-jammy`.
*   **Scheduling**: Linux `cron` runs inside the container.
*   **Environment**:
    *   `.env` file is used for secrets (Bot API, Group ID).
    *   `TZ=Asia/Manila` is critical for correct scheduling.
*   **Volumes**: `./images` is persisted to store/track processed images.

## 🛠 Commands

*   `docker compose up --build -d`: Rebuild and start the service.
*   `docker logs -f noreco_power_outage`: View logs.
*   `docker exec -it noreco_power_outage bash`: Enter container.

## 📌 Development Notes

*   **Telegram Stars**: Integration in progress. Requires an active bot session for handling payments (polling or webhooks), whereas the current script is short-lived.
*   **OCR**: Text extraction logic exists but is currently disabled in the main flow.
