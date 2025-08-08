# 🔌 Noreco Power Outage Monitor

An automated system that monitors power outage announcements from Noreco's website, extracts images, performs OCR text recognition, and sends notifications to Telegram.

## ✨ Features

- 🌐 **Web Scraping**: Automatically extracts power outage images from Noreco's carousel
- 📥 **Image Download**: Downloads and saves all outage announcement images
- 🔍 **OCR Processing**: Extracts text from images using EasyOCR
- 📱 **Telegram Integration**: Sends processed images to Telegram group
- 🐳 **Docker Support**: Containerized deployment ready

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
# Logging
LOG_LEVEL=INFO

# Telegram Settings
TELEGRAM_BOT_API=your_bot_token_here
TELEGRAM_GROUP_ID=your_group_id_here

# Website Configuration
URL=https://www.noreco2.com.ph/power-outage
MEDIA_FILE_ON_SITE_PATTERN=https://static\.wixstatic\.com/media/[^\"\'\\s>\\\\]+?\.jpg
IMAGES_DIR=images
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Parser    │───▶│  Image Saver    │───▶│   OCR Engine    │
│  (wix_parser)   │    │(save_images_*)  │    │   (easyocr)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐             │
│ Telegram Sender │◀───│  Main Process   │◀────────────┘
│(telegram_sender)│    │    (main.py)    │
└─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
NorecoPowerOutage/
├── main.py                    # Main application entry point
├── wix_parser.py             # Web scraping and carousel navigation
├── save_images_from_links.py # Image downloading functionality
├── easyocr.py                # OCR text recognition
├── telegram_sender.py        # Telegram bot integration
├── config.py                 # Configuration management
├── logger.py                 # Logging setup
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker composition
├── Dockerfile               # Container definition
└── images/                  # Downloaded images directory
```

## 🔧 Usage

### Basic Usage

```python
import asyncio
from main import main

# Run the complete pipeline
asyncio.run(main())
```

### Individual Components

```python
# Web scraping only
from wix_parser import extract_from_page
links = await extract_from_page("https://www.noreco2.com.ph/power-outage")

# Image downloading only
from save_images_from_links import save_images
paths = save_images(links)

# OCR processing only
from easyocr import recognize_text_in_folder
recognize_text_in_folder(Path("images"))

# Telegram sending only
from telegram_sender import send_images_to_group
await send_images_to_group(image_paths)
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

- **playwright** - Web automation and scraping
- **requests** - HTTP client for image downloads
- **aiogram** - Telegram Bot API framework
- **easyocr** - Optical Character Recognition
- **pydantic-settings** - Configuration management
- **Pillow** - Image processing

## 🔍 How It Works

1. **Web Scraping**: Uses Playwright to navigate the Noreco website carousel and extract image URLs
2. **Image Processing**: Downloads images and applies enhancement (grayscale, contrast boost)
3. **Text Recognition**: Performs OCR on processed images to extract text content
4. **Notification**: Sends both images and extracted text to configured Telegram group

## 🛠️ Development

### Running Tests

```bash
# Run individual modules
python wix_parser.py
python save_images_from_links.py
python easyocr.py
```

### Logging

The application uses structured logging with configurable levels:

```python
from logger import logger
logger.info("Processing started")
logger.debug("Detailed debug information")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions, please open an issue on the repository.

---

*Built with ❤️ for automated power outage monitoring*