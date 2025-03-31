import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID администраторов, которые могут получать аналитику
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Параметры базы данных
DB_NAME = 'feedback_bot.db'

# Категории продуктов/услуг
PRODUCT_CATEGORIES = [
    "Смартфоны",
    "Ноутбуки",
    "Наушники",
    "Умные часы",
    "Планшеты",
    "Аксессуары",
    "Доставка",
    "Обслуживание клиентов",
    "Другое"
]