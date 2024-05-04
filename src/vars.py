import os
from dotenv import load_dotenv


load_dotenv('.env')


K_0_75 = """
😞Не переживай, в b0 уже есть %s человек, с которыми у тебя крепость дружбы больше 75%%.
Подписывайся на [наш тг канал](https://t.me/bo_app), чтобы узнать первым дату выхода приложения. 

📱[Что такое приложение b0?](https://gband.app/)

🤔[Почему этим данным стоит доверять?](https://telegra.ph/Mesto-gde-tebya-cenyat-po-nastoyashchemu-04-27)
"""


K_75_100 = """
🎉Здорово, в b0 ещё %s людей, с которыми ты построишь такие же классные отношения. 
Подписывайся на [наш тг канал](https://t.me/bo_app), чтобы узнать первым дату выхода приложения. 

📱[Что такое приложение b0?](https://gband.app/)

🤔[Почему этим данным стоит доверять?](https://telegra.ph/Mesto-gde-tebya-cenyat-po-nastoyashchemu-04-27)
"""


LOGIN_NOT_FOUND_MESSAGE = "Пожалуйста, установите имя пользователя в настройках телеграм"

AUTH_SUCCESS = f"""
Отлично! 👍🏻

Дальше всё в твоих руках. Вспоминай делать глубокий вдох удивления от захватывающих знакомств!
До встречи в b0. 👋

P.S. Твой код для входа: `%s`
"""

ONBOARDING_REQUIRED = f"""
На сколько крепкая твоя дружба?

На этот вопрос ответит лучший алгоритм совместимости b0. Для этого ему нужно немного инфы о тебе.

Нажми на кнопку внизу "дать инфо" 👇
"""

SELECT_FRIEND_REQUEST = f"""
Ты на верном пути: выбери друга, 
чтобы узнать насколько у вас крепкая дружба
"""

DONT_UNDERSTAND = f"""
Я не понимаю 😢
"""

USER_NOT_FOUND = f"""
У нас нет информации о Твоем друге.

Чтобы увидеть, насколько крепка ваша дружба, алгоритму нужно знать его ценности и дату рождения.

Отправь ссылку на бота @bo_app_bot своему другу и попроси оставить инфо. 
Как ты уже понял, это займет меньше 5 минут, зато вы узнаете крепость вашей дружбы с точностью до 100%%
"""

BACK_TO_APP_BUTTON = """Вернуться в приложение 📲"""

SIGNUP_FINISHED_REQUIRED_BUTTON = """Дать инфу алгоритму b0 ✍️"""

SELECT_FRIEND_BUTTON = """Выбрать друга 👤"""

MAIN_MENU_BUTTON = """В главное меню 🔙"""

PRODUCTION_STATUS = """Статус разработки «bo» 🔩"""

FAMOUES_FRIEND_BUTTON = """Кто мой друг из знаменитостей 👑"""

NO_FAMOUS_FRIENDS_FOUND = """Похоже сейчас все звезды спят 😴 заходи ночью 🌃"""

K_FRIENDSHIP_EXPLANATION = """
🧠[Как работает алгоритм b0?](https://t.me/bo_app/71)

🤔[Почему данным стоит доверять b0?](https://t.me/bo_app/71) 

😭[Что делать, если результат меня расстроил?](https://t.me/bo_app/71)

👍Что делать, если результат меня порадовал?(конечно подписаться на [@bo_app])
"""

FAMOUS_FRIEND_K_RESULT = """
C %s у тебя была бы самая крепкая дружба. 💯 

Мы рекомендуем сообщить %s как-то эту новость. 
Размести эту пикчу в сторис и отметь его аккаунт. 📸 

Вдруг - это судьба? 🤔
"""

MAIN_MENU_TEXT = """Скорее выбирай то, зачем пришел 👇"""


PRODUCTION_STATUS_TEXT = """
🔩 Статус разработки «bo»

Готовность:

🧩  IOS версия - 83 🛍
🧩  Android версия - 67 🛍
🧩  Web версия - 62 🛍

📆Приблизительная дата релиза приложения: 

Июнь 2024 года

Почему b0 - лучшее приложение для *настоящих* знакомств? Ответ тут 👉 [@bo_app]
"""
