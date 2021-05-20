import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.common import register_handlers_common
from app.handlers.location import register_handlers_location
from app.services.db import init_db
from config import BOT_TOKEN, ADMIN_ID

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    # команды бота
    commands = [
        BotCommand(command='/start', description='Запустить бота'),
        BotCommand(command='/help', description='Помощь'),
    ]
    await bot.set_my_commands(commands)


async def bot_started(bot: Bot):
    await bot.send_message(chat_id=ADMIN_ID, text='Бот Запущен')


async def main():
    # настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    logger.error('Starting bot')

    # Инициализируем бота и диспетчера
    bot = Bot(token=BOT_TOKEN, parse_mode='html')
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers_common(dp, ADMIN_ID)
    register_handlers_location(dp)

    # Установка команд бота
    await set_commands(bot)

    await bot_started(bot)
    await init_db()

    # Запуск поллинга
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
