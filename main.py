import os
from aiohttp import web
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.flags import get_flag
from src.handlers import router, handle_apple_id
from src.auth import AuthorizationMiddleware
from src.cache import RedisConnector
from src import preload
from bot import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src import schedule


load_dotenv('.env')


async def start_web_server():
    app = web.Application()
    app.router.add_post("/auth/", handle_apple_id)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8123)
    await site.start()
    print("Web server started on http://0.0.0.0:8123")


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AuthorizationMiddleware())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await RedisConnector.connect()

        if not os.environ.get("DEBUG", False):
            await asyncio.gather(
                preload.preload_stars(),
                preload.preload_stars_photos(),
                preload.preload_stars_k_results(),
                preload.preload_friends_k_results()
            )

        await asyncio.gather(
            dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types()
            ),
            start_web_server()
        )
    finally:
        await RedisConnector.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
