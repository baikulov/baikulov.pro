# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = '6894040586:AAG9efYDbFa9JkDRyzbNl3Z72b27qazrglY'
# Замените 'YOUR_CHANNEL_ID' на ID вашего канала
CHANNEL_ID = '-1002113163128'  # Замените на ваш username или ID канала
# Замените 'YOUR_RSS_URL' на URL вашей RSS-ленты
RSS_URL = 'https://baikulov.github.io/wiki/feed_rss_updated.xml'
import asyncio
import feedparser
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from html import unescape
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

async def send_to_telegram(title, description, link):
    bot = Bot(token=BOT_TOKEN)

    # Удаляем HTML-теги из описания
    soup = BeautifulSoup(description, 'html.parser')

    # Извлекаем URL изображения из тега <img>
    image_tag = soup.find('img')
    image_url = None
    if image_tag:
        base_url = 'https://baikulov.github.io/wiki/blog/_attachments/'
        image_url = urljoin(base_url, image_tag.get('src').split("/")[-1])

    cleaned_description = soup.find('p').get_text(strip=True)

    # Декодирование HTML-сущностей
    cleaned_description = unescape(cleaned_description)

    # Используем Markdown-разметку для форматирования сообщения
    message = f"*{title}*\n\n{cleaned_description}\n\n[Читать далее]({link})"

    try:
        # Загружаем изображение и отправляем его вместе с сообщением
       # Загружаем изображение и отправляем его вместе с сообщением
        if image_url:
            print(f"Изображение успешно скачано: {image_url}")
            print(cleaned_description)
            image_data = requests.get(image_url).content
            if image_url.startswith('https://baikulov.github.io/wiki/blog/'):
                await bot.send_photo(chat_id=CHANNEL_ID, photo=image_data, caption=message, parse_mode=ParseMode.MARKDOWN)
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)
        else:
            print("Изображение не найдено.")
            await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    except TelegramError as e:
        print(f"Ошибка при отправке сообщения: {e}")

async def check_rss_feed(RSS_URL):
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries:
        if not is_post_published(entry.link):
            await send_to_telegram(entry.title, entry.description, entry.link)

def is_post_published(link):
    # Ваш код для проверки, была ли запись уже опубликована
    pass

async def main():
    rss_feed_url = RSS_URL
    await check_rss_feed(rss_feed_url)

asyncio.run(main())