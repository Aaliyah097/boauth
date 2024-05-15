import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.flags import get_flag
from src.handlers import router
from src.auth import AuthorizationMiddleware
from src.cache import RedisConnector
from src import preload


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

    try:
        await RedisConnector.connect()

        try:
            await preload.preload_stars()
        except Exception as e:
            pass

        # try:
        #     await preload.preload_stars_photos()
        # except Exception as e:
        #     pass

        # try:
        #     await preload.preload_stars_k_results()
        # except Exception as e:
        #     pass

        # try:
        #     await preload.preload_friends_k_results()
        # except Exception as e:
        #     pass

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await RedisConnector.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
