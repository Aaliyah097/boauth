from bot import bot
from src.api_requests import list_users
import os
import aiogram.exceptions
from dotenv import load_dotenv
import json
import aiofiles


load_dotenv('.env')


async def calc_members():
    users, members = await list_users(), 0
    for user in users:
        try:
            member = await bot.get_chat_member(
                chat_id=os.environ.get("CHANNEL_ID"),
                user_id=int(user['id_tg'] or 0)
            )
            if member.status == 'member':
                members += 1
        except aiogram.exceptions.TelegramBadRequest as e:
            pass

    async with aiofiles.open(f"{os.environ.get('CHANNEL_ID')}.json", mode='wb') as f:
        await f.write(
            json.dumps({
                'users': len(users),
                'members': members
            }).encode('utf-8')
        )
