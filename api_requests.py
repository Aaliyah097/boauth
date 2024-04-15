import os
import random
from string import ascii_letters
from dotenv import load_dotenv
from httpx import AsyncClient
from utils import encrypt_api_key
from exceptions import UserNotFoundError
from models import Account


load_dotenv('.env')

host = os.environ.get("API_HOST")
headers = {
    "x-api-key": encrypt_api_key(os.environ.get("API_KEY")),
}


async def get_jwt_pair() -> tuple[str, str]:
    async with AsyncClient(base_url=host, verify=False) as client:
        response = await client.post(
            '/api/auth/token/create/',
            json={
                "login_tg": os.environ.get("ADMIN_TG"),
                "password": os.environ.get("ADMIN_PASSWORD")
            }
        )
        if not response.status_code == 200:
            response.raise_for_status()

        response = response.json()
        return response.get('access'), response.get('refresh')


async def get_account(telegram_login: str) -> Account:
    async with AsyncClient(base_url=host, verify=False) as client:
        response = await client.get(
            f"/api/accounts/?telegram={telegram_login}",
            headers=headers
        )
        if response.status_code != 200:
            response.raise_for_status()
        response = response.json()
        if len(response) == 0:
            raise UserNotFoundError("Пользователь не найден")
        print(response)
        return Account(
            # pk=response[0]['id'],
            login_tg=response[0]['login_tg'],
            id_tg=str(response[0]['id_tg']) if response[0]['id_tg'] else None,
            is_active=response[0]['is_active'],
            is_onboarded=response[0]['is_onboarded']
        )


async def activate_account(account_id: int, telegram_id: str) -> None:
    async with AsyncClient(base_url=host, verify=False) as client:
        response = await client.post(
            f"/api/accounts/{account_id}/activate/",
            headers=headers,
            json={
                "telegram_id": str(telegram_id)
            }
        )
        match response.status_code:
            case 404:
                raise UserNotFoundError("Пользователь или инвайт не найдены")
            case 200:
                pass
            case _:
                response.raise_for_status()


async def signup_user(tg_username: str, tg_id: str) -> Account:
    password = "".join([random.choice(ascii_letters) for _ in range(8)])

    return Account(
        login_tg=tg_username,
        id_tg=tg_id,
        is_active=True,
        is_onboarded=False
    )
