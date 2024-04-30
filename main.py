import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.flags import get_flag
from src.handlers import router
from src.auth import AuthorizationMiddleware


load_dotenv('.env')


async def main():
    bot = Bot(
        parse_mode='Markdown',
        token=os.environ.get('BOT_TOKEN')
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AuthorizationMiddleware())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
