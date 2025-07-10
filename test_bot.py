#!/usr/bin/env python3
"""
Простой тест для проверки работы бота без job_queue
"""
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_start(update, context):
    """Простая тестовая команда"""
    await update.message.reply_text("Бот работает! ✅")

async def setup_commands(application):
    """Установить команды меню"""
    try:
        from telegram import BotCommand
        commands = [
            BotCommand("start", "🚀 Тест бота"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("Команды установлены успешно")
    except Exception as e:
        logger.warning(f"Ошибка установки команд: {e}")

if __name__ == '__main__':
    TOKEN = os.getenv('TELEGRAM_TOKEN') or '7799371983:AAEa3w1CGc6BwUcWG2MoVxfL5bJOgg8OhJ4'
    
    # Создаем приложение
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчик
    app.add_handler(CommandHandler('start', test_start))
    
    # Устанавливаем команды при запуске (без job_queue)
    try:
        import asyncio
        asyncio.create_task(setup_commands(app))
    except Exception as e:
        logger.warning(f"Не удалось установить команды: {e}")
    
    logger.info("Тестовый бот запускается...")
    app.run_polling() 