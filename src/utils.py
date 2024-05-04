from typing import Awaitable
import os
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


cipher_suite = Fernet(os.environ.get("ENCRYPTION_KEY").encode())


class StartParamEnum(str, Enum):
    mobile = "mobile"
    web = "web"


async def download_photo(link: str) -> bytes:
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
    return (telegram_id % (10 - 3 + 1)) + 3


async def make_star_k_picture(k: int, star_photo: bytes) -> BytesIO:
    k, png_output = normalize_k(k), BytesIO()

    async with aiofiles.open('static/k_star.svg', 'rb') as file:
        svg_content = await file.read()
        svg_content = svg_content.replace(
            b"{{percent}}",
            str(k).encode('utf-8')
        ).replace(
            b"{{picture}}",
            star_photo
        )

        cairosvg.svg2png(
            bytestring=svg_content,
            write_to=png_output,
            background_color='black'
        )

    png_output.seek(0)
    return png_output


async def make_friend_k_picture(k: int) -> BytesIO:
    k, png_output = normalize_k(k), BytesIO()
    if k < 50:
        picture_name = '0-49.svg'  # TODO
    elif k < 75:
        picture_name = '50-74.svg'  # TODO
    else:
        picture_name = '75-100.svg'

    async with aiofiles.open(f'static/{picture_name}', 'rb') as file:
        svg_content = await file.read()
        svg_content = svg_content.replace(
            b"{{percent}}",
            str(k).encode('utf-8')
        )

        cairosvg.svg2png(
            bytestring=svg_content,
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
        await connection.expire(nonce, 15 * 60)
        return str(nonce)


def is_valid_url(url: str) -> bool:
    if url.startswith("https") or url.startswith("tg"):
        return True
    return False
