import time
from typing import Awaitable
import os
import json
import base64
from io import BytesIO
from enum import Enum
import random
import cairosvg
import aiofiles
from httpx import AsyncClient
from cryptography.fernet import Fernet
from src.cache import RedisConnector
from src.exceptions import UnknownError
from src import vars
from src.cache import RedisConnector
from src.models import StarProfile


cipher_suite = Fernet(os.environ.get("ENCRYPTION_KEY").encode())
ZVEZDA_PICTURE = None
RAT_49 = None
RAT_75 = None
RAT_100 = None

USER_CHECKS_KEY = "user_%s_checks"
CHECKS_FOR_REWARD = int(os.environ.get("CHECKS_FOR_REWARD", 5))


class StartParamEnum(str, Enum):
    mobile = "mobile"
    web = "web"


def get_checks_message(checks_left: int) -> str:
    checks_map = {
        5: '5️⃣',
        4: '4️⃣',
        3: '3️⃣',
        2: '2️⃣',
        1: '1️⃣'
    }

    if checks_left > CHECKS_FOR_REWARD:
        checks_left = CHECKS_FOR_REWARD

    if checks_left not in checks_map:
        return vars.NO_CHECKS_LEFT
    elif checks_left == 2:
        return vars.CHECKS_FOR_REWARD_2
    elif checks_left == 1:
        return vars.CHECKS_FOR_REWARD_1
    else:
        return vars.CHECKS_FOR_REWARD % checks_map[checks_left]


async def get_checks_left_for_reward(user_id: str) -> int:
    user_id = str(user_id)

    async with RedisConnector() as connection:
        current_checks = await connection.scard(USER_CHECKS_KEY % str(user_id))
        return max(CHECKS_FOR_REWARD - current_checks, 0)


async def add_user_check_for_reward(user_id: str, friend_id: str) -> int:
    user_id, friend_id = str(user_id), str(friend_id)

    async with RedisConnector() as connection:
        await connection.sadd(USER_CHECKS_KEY % str(user_id), friend_id)

    return await get_checks_left_for_reward(user_id)


async def download_photo(link: str) -> bytes:
    async with RedisConnector() as r_client:
        res = await r_client.get(link)
        if res:
            return json.loads(res.decode('utf-8'))['link'].encode('utf-8')

    async with AsyncClient(verify=False) as client:
        response = await client.get(
            url=link
        )
        match response.status_code:
            case 200:
                return base64.b64encode(response.content)
            case _:
                UnknownError("Ой-ой...Что-то пошло не так 😰")


def normalize_k(k: int) -> int:
    try:
        k = int(k)
    except ValueError:
        k = 0

    if k > 99:
        k = 99
    if k < 10:
        k = 10

    return k


def get_k_message(k: int) -> str:
    if k >= 75:
        return vars.K_75_100
    return vars.K_0_75


def get_id_number(telegram_id: int) -> int:
    min_value, max_value, hash_value = 5, 10, hash(telegram_id)
    return (min_value + (hash_value % (max_value - min_value + 1)))


async def make_star_k_picture(k: int, star: StarProfile) -> BytesIO:
    global ZVEZDA_PICTURE
    if not ZVEZDA_PICTURE:
        async with aiofiles.open('static/zvezda.svg', 'rb') as file:
            ZVEZDA_PICTURE = await file.read()

    k, png_output, key, star_photo = (
        normalize_k(k),
        BytesIO(),
        f'star_{str(k)}_{str(star.id_tg)}',
        await download_photo(star.photo)
    )

    async with RedisConnector() as client:
        content = await client.get(key)
        if content:
            png_output = BytesIO(content)
        else:
            cairosvg.svg2png(
                bytestring=ZVEZDA_PICTURE.replace(
                    b"{{percent}}",
                    str(k).encode('utf-8')
                ).replace(
                    b"{{picture}}",
                    star_photo or b''
                ),
                write_to=png_output,
                background_color='black'
            )

    png_output.seek(0)

    return png_output


async def make_friend_k_picture(k: int) -> BytesIO:
    global RAT_100, RAT_75, RAT_49

    k, png_output, svg_content, key = (
        normalize_k(k),
        BytesIO(),
        b'',
        f"friend_{str(k)}"
    )

    if k < 50:
        if not RAT_49:
            async with aiofiles.open(f'static/0-49.svg', 'rb') as file:
                RAT_49 = await file.read()
        svg_content = RAT_49
    elif k < 75:
        if not RAT_75:
            async with aiofiles.open(f'static/50-74.svg', 'rb') as file:
                RAT_75 = await file.read()
        svg_content = RAT_75
    else:
        if not RAT_100:
            async with aiofiles.open(f'static/75-100.svg', 'rb') as file:
                RAT_100 = await file.read()
        svg_content = RAT_100

    async with RedisConnector() as client:
        content = await client.get(key)
        if content:
            png_output = BytesIO(content)
        else:
            cairosvg.svg2png(
                bytestring=svg_content.replace(
                    b"{{percent}}", str(k).encode('utf-8')),
                write_to=png_output,
                background_color='black'
            )

    png_output.seek(0)
    return png_output


def encrypt_api_key(api_key) -> str:
    return cipher_suite.encrypt(str.encode(api_key)).decode('utf-8')


def verify_login(login: str) -> str:
    if not login:
        raise ValueError("Логин не указан")
    if "t.me" in login:
        login = login.split("/")[-1]
    if not login.startswith("@"):
        return f"@{login}"
    return login


def make_nonce(strength: int = 6) -> str:
    digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    return "".join(str(random.choice(digits)) for _ in range(strength))


async def store_telegram_id(nonce: str, telegram_id: str) -> str:
    async with RedisConnector() as connection:
        await connection.set(nonce, str(telegram_id))
        await connection.expire(nonce, 1 * 60 * 60 * 24 * 7)
        return str(nonce)


async def clean_telegram_id(nonce: str) -> str:
    async with RedisConnector() as connection:
        await connection.delete(nonce)


def is_valid_url(url: str) -> bool:
    if url.startswith("https") or url.startswith("tg"):
        return True
    return False
