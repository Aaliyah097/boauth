import os
from typing import Union
import random
from cryptography.fernet import Fernet
from cache import RedisConnector


cipher_suite = Fernet(os.environ.get("ENCRYPTION_KEY").encode())


async def get_start_params(nonce: str) -> str | None:
    if not nonce:
        return None
    async with RedisConnector() as connection:
        redirect_uri = await connection.get(nonce)
        return redirect_uri.decode('utf-8') if redirect_uri else None


def encrypt_api_key(api_key) -> str:
    return cipher_suite.encrypt(str.encode(api_key)).decode('utf-8')


def verify_login(login: str) -> str:
    if not login:
        raise ValueError("Логин не указан")
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
