import asyncio
from datetime import datetime
import feedparser
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from html import unescape, escape
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import logging
import os

# токен вашего бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
# ID вашего канала
CHANNEL_ID = os.getenv('CHANNEL_ID')  # Замените на ваш username или ID канала
# URL вашей RSS-ленты
RSS_URL = os.getenv('RSS_URL')

logging.basicConfig(level=logging.INFO)

async def send_to_telegram(bot, title, description, link, tags):
    # Удаляем HTML-теги из описания
    soup = BeautifulSoup(description, 'html.parser')

    # Извлекаем URL изображения из тега <img>
    image_tag = soup.find('img')
    image_url = urljoin('https://baikulov.github.io/wiki/blog/_attachments/', image_tag.get('src').split("/")[-1]) if image_tag else None

    cleaned_description = soup.find('p').get_text(strip=True)

    # Декодирование HTML-сущностей
    cleaned_description = escape(cleaned_description)

    escaped_tags = [str(tag).replace('_', r'\_').replace('*', r'\*').replace('[', r'\[').replace(']', r'\]') for tag in tags]
    tags_text = " ".join([f"#{tag}" for tag in escaped_tags]) if escaped_tags else ""

    # Используем Markdown-разметку для форматирования сообщения
    message = f"*{title.upper()}*❗\n{tags_text}\n\n{cleaned_description}\n\n[Читать на сайте]({link})"

    try:
        if image_url:
            logging.info(f"Изображение успешно скачано: {image_url}")
            image_data = requests.get(image_url).content
            send_function = bot.send_photo if image_url.startswith('https://baikulov.github.io/wiki/blog/') else bot.send_message
            await send_function(chat_id=CHANNEL_ID, photo=image_data, caption=message, parse_mode=ParseMode.MARKDOWN)
        else:
            logging.warning("Изображение не найдено.")
            await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)

    except TelegramError as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

async def check_rss_feed(bot, RSS_URL):
    feed = feedparser.parse(RSS_URL)
    current_date = datetime.utcnow().date()
    if feed.entries:
        entry = feed.entries[0]
        pub_date_str = entry.get('published', '')
        date_format = "%a, %d %b %Y %H:%M:%S %z"
        pub_date = datetime.strptime(pub_date_str, date_format).date()
        if pub_date == current_date:
            tags = [category.term for category in entry.get('tags', [])]
            await send_to_telegram(bot, entry.title, entry.description, entry.link, tags=tags)


async def main():
    bot = Bot(token=BOT_TOKEN)
    await check_rss_feed(bot, RSS_URL)

asyncio.run(main())