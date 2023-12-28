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

async def send_to_telegram(title, description, link):
    bot = Bot(token=BOT_TOKEN)

    # Удаляем HTML-теги из описания
    soup = BeautifulSoup(description, 'html.parser')
    cleaned_description = soup.get_text()

    # Извлекаем URL изображения (если есть)
    image_url = None
    image_tag = soup.find('img')
    if image_tag:
        image_url = image_tag.get('src')

    # Декодирование HTML-сущностей
    cleaned_description = unescape(cleaned_description)

    # Добавляем изображение к текстовому сообщению (если есть)
    if image_url:
        cleaned_description += f'\n[Изображение]({image_url})'

    # Используем Markdown-разметку для форматирования сообщения
    message = f"\n{cleaned_description}\n\n[Читать далее]({link})"

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)
        print(f"Сообщение успешно отправлено: {title}")
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

if __name__ == "__main__":
    asyncio.run(main())