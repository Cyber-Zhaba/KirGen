# KirGen-VS-ORC
Help you with russian tasks with tesseract-orc and [gramota.ru](https://gramota.ru)

Powered by [Tesseract](https://tesseract-ocr.github.io).
Used [rus.traineddata](https://github.com/tesseract-ocr/tessdata/blob/main/rus.traineddata)

## What's new?
- Global refactoring
- Project restructuring
- Added Telegram bot
- Added config.yaml file
- Code check with ruff
- Added ruff.toml file

## Installation
1. Install [Python 3.11](https://www.python.org/downloads/)
2. Install [Tesseract](https://tesseract-ocr.github.io/tessdoc/Downloads.html)
3. Install [rus.traineddata](https://github.com/tesseract-ocr/tessdata/blob/main/rus.traineddata)
4. Install `requirements.txt`
5. Run `source/scraper.py`

## Telegram bot
Bot uses API from api module.
Developed for only private chats.
By default, uses russian language, but you can change it in `TelegramBot/botReplicas.py`

## TODO
- Add web interface
- Add more sites for word spelling search