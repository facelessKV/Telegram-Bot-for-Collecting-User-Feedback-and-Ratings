import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, DB_NAME
from database import Database
from handlers import router  # Импортируем роутер из handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Асинхронная функция запуска бота
    """
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    db = Database(DB_NAME)
    db.create_tables()
    logger.info("База данных инициализирована")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутера
    dp.include_router(router)
    
    # Запуск поллинга
    logger.info("Бот запущен и готов к работе!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())