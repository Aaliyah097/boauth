import os
from dotenv import load_dotenv


load_dotenv('.env')


LOGIN_NOT_FOUND_MESSAGE = "Пожалуйста, установите имя пользователя в настройках телеграм"

AUTH_SUCCESS = f"""
Отлично, %s! 👍🏻\n

Дальше всё в твоих руках. Вспоминай делать глубокий вдох удивления от захватывающих знакомств!\n

До встречи в b0. 👋\n

P.S. Твой код для входа: <strong>%s</strong>
"""

ONBOARDING_REQUIRED = f"""
Так это же круто, %s! 👍🏻\n
Но надо закончить регистрацию. \n
Для этого нажимай на кнопку ниже\n

P.S. Твой код для завершения регистрации: <strong>%s</strong>
"""

NOTHING_REQUIRED = f"""
Окэй, %s!
Ничего не требуется
"""

SELECT_FRIEND_REQUEST = f"""
%s, \n
Пришли мне телеграм ID друга или ссылку на его аккаунт
"""

DONT_UNDERSTAND = f"""
%s, \n
Я не понимаю :(
"""

FRIENDSHIP_STRENGTH = f"""
%s, \n
Твой коэффициент дружбы с %s равен %s
"""