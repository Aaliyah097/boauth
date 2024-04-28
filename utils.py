import os
from io import BytesIO
from enum import Enum
import random
import cairosvg
import aiofiles
from cryptography.fernet import Fernet
from cache import RedisConnector
import vars

cipher_suite = Fernet(os.environ.get("ENCRYPTION_KEY").encode())


class StartParamEnum(str, Enum):
    mobile = "mobile"
    web = "web"


async def make_friend_k_picture(k: int) -> BytesIO:
    png_output = BytesIO()
    async with aiofiles.open('static/friend_k copy.svg', 'rb') as file:
        svg_content = await file.read()
        svg_content = svg_content.replace(
            "{{percent}}".encode('utf-8'),
            f"{k}".encode('utf-8')
        )

        cairosvg.svg2png(bytestring=svg_content,
                         write_to=png_output, background_color='black')

    png_output.seek(0)
    return png_output


def encrypt_api_key(api_key) -> str:
    return cipher_suite.encrypt(str.encode(api_key)).decode('utf-8')


def verify_login(login: str) -> str:
    # https://t.me/echpochiMac
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
        return nonce


def is_valid_url(url: str) -> bool:
    if url.startswith("https") or url.startswith("tg"):
        return True
    return False
