import os
from aiogram import Bot
from dotenv import load_dotenv


load_dotenv('.env')


bot = Bot(
    parse_mode='Markdown',
    token=os.environ.get('BOT_TOKEN')
)
