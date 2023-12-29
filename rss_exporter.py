import asyncio
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

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
print(BOT_TOKEN)
# Замените 'YOUR_CHANNEL_ID' на ID вашего канала
CHANNEL_ID = os.getenv('CHANNEL_ID')  # Замените на ваш username или ID канала
# Замените 'YOUR_RSS_URL' на URL вашей RSS-ленты
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

    # Экранирование символа * в описании
    cleaned_description = cleaned_description.replace('*', r'\*')

    tags_text = " ".join([f"#{escape(tag)}" for tag in tags]) if tags else ""

    # Экранирование символа * в каждом теге
    tags_text = tags_text.replace('*', r'\*')

    # Экранирование символа * в заголовке
    title = escape(title).replace('*', r'\*')

    # Используем Markdown-разметку для форматирования сообщения
    message = f"*{title}*\n{tags_text}\n\n{cleaned_description}\n\n[Читать далее]({link})"

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
        # Добавьте вывод описания статьи для отладки
        logging.error(f"Описание статьи: {description}")
        logging.error(f"Текст сообщения: {message}")
        logging.error(f"CHANNEL_ID: {CHANNEL_ID}")

async def check_rss_feed(bot, RSS_URL):
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries:
        if not is_post_published(entry.link):
            tags = [category.term.lower() for category in entry.get('tags', [])]
            await send_to_telegram(bot, entry.title, entry.description, entry.link, tags=tags)

def is_post_published(link):
    # Ваш код для проверки, была ли запись уже опубликована
    pass

async def main():
    bot = Bot(token=BOT_TOKEN)
    await check_rss_feed(bot, RSS_URL)

asyncio.run(main())