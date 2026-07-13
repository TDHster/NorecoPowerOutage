# 🔌 Noreco Power Outage Monitor

Automated system that monitors power outage announcements from Noreco's website, extracts images, and sends notifications to Telegram.

## ✨ Features

- 🌐 **Web Scraping**: Automatically extracts power outage images from Noreco's carousel
- 📥 **Image Download**: Downloads and saves new outage announcement images
- 📱 **Telegram Integration**: Sends processed images to Telegram group
- 🧹 **Auto-cleanup**: Removes local images no longer present on the site
- 🐳 **Docker Support**: Containerized deployment via cron

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Telegram Bot Token
- Telegram Group/Channel ID

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NorecoPowerOutage
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
LOG_LEVEL=INFO
TELEGRAM_BOT_API=your_bot_token_here
TELEGRAM_GROUP_ID=your_group_id_here
URL=https://www.noreco2.com.ph/power-outage
MEDIA_FILE_ON_SITE_PATTERN=https://static\.wixstatic\.com/media/[^\"\'\\s>\\\\]+?\.jpg
IMAGES_DIR=images
```

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Web Parser   │───▶│ Image Saver  │───▶│   Telegram   │
│ (wix_parser) │    │(save_images) │    │   Sender     │
└──────────────┘    └──────────────┘    └──────────────┘
       │                                        │
       └──── main.py orchestrates ──────────────┘
```

## 📁 Project Structure

```
NorecoPowerOutage/
├── main.py                    # Main application entry point
├── wix_parser.py             # Web scraping and carousel navigation
├── save_images_from_links.py # Image downloading functionality
├── telegram_sender.py        # Telegram bot integration
├── remove_nonlist_file.py    # Cleanup of stale images
├── config.py                 # Configuration management
├── logger.py                 # Logging setup
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container definition
├── docker-compose.yml        # Docker composition
├── barangays.csv             # Reference list of municipalities (for future use)
├── develop_ocr_for_agent.md  # OCR pipeline specification (for future use)
└── images/                  # Downloaded images directory
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run with Docker directly
docker build -t noreco-monitor .
docker run --env-file .env noreco-monitor
```

## 📋 Dependencies

- **playwright** — Web automation and scraping
- **requests** — HTTP client for image downloads
- **aiogram** — Telegram Bot API framework
- **pydantic-settings** — Configuration management

## 🔍 How It Works

1. **Web Scraping**: Playwright navigates the Noreco website carousel and extracts image URLs
2. **Image Processing**: Downloads new images, removes stale ones
3. **Notification**: Sends images to configured Telegram group

## 🛠️ Development

### Logging

```python
from logger import logger
logger.info("Processing started")
logger.debug("Detailed debug information")
```

---

*Built with ❤️ for automated power outage monitoring*