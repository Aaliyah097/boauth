import os
from dotenv import load_dotenv


load_dotenv('.env')


LOGIN_NOT_FOUND_MESSAGE = "Пожалуйста, установите имя пользователя в настройках телеграм"
START_CODE_NOT_FOUND=f"""
Рад тебя встретить здесь 👋 Ты на верном пути!\n

Только для доступа в <a href="{os.environ.get('WEB_SITE_URI')}">b0</a> 
нужно попасть по ссылке из сервиса.\n

📱<a href="{os.environ.get('APP_STORE_LINK')}">Скачай</a> приложение на iPhone или 
зайди через 🌐 <a href="{os.environ.get('PWA_LINK')}">сайт</a>\n

Поспеши, я уже жду тебя 🫶.
"""
USER_NOT_FOUND = f"""
Похоже, твоя Карма пока не готова для судьбоносных встреч. 😞\n

Узнай, как можно это исправить уже <a href="{os.environ.get('INVITE_SERVICE_LINK')}">сейчас</a>!
"""
AUTH_SUCCESS = f"""
Отлично, %s! 👍🏻\n

Дальше всё в твоих руках. Вспоминай делать глубокий вдох удивления от захватывающих знакомств!\n

До встречи в b0. 👋\n

P.S. Твой код для входа: <strong>%s</strong>
"""