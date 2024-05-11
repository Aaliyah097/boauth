import os
import random
from copy import copy
from string import ascii_letters
from dotenv import load_dotenv
from httpx import AsyncClient
from src.utils import encrypt_api_key
from src.exceptions import UserNotFoundError, SignupFailedException, UnknownError
from src.models import Account, StarProfile


load_dotenv('.env')

host = os.environ.get("API_HOST")
headers = {
    "x-api-key": encrypt_api_key(os.environ.get("API_KEY")),
}


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
        return Account(
            login_tg=response[0]['login_tg'],
            id_tg=str(response[0]['id_tg']) if response[0]['id_tg'] else None,
            is_onboarded=response[0]['is_onboarded'],
            vocabulary_category=response[0]['vocabulary_category'],
            birthday=response[0]['birthday'],
            values=response[0]['values'],
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
    h = copy(headers)
    h['Content-Type'] = 'application/x-www-form-urlencoded'

    if not tg_username.startswith("@"):
        tg_username = "@" + tg_username

    async with AsyncClient(base_url=host, verify=False) as client:
        response = await client.post(
            "/api/accounts/register/",
            headers=h,
            data={
                "login_tg": tg_username,
                'id_tg': tg_id,
                'password': "".join([random.choice(ascii_letters) for _ in range(8)])
            }
        )
        if response.status_code != 201:
            raise SignupFailedException(response.text)

    return Account(
        login_tg=tg_username,
        id_tg=tg_id,
        is_onboarded=False,
        birthday=None,
        values=[],
        vocabulary_category=None
    )


async def calc_friendship_k(telegram_id_user: int, telegram_id_friend: int) -> int:
    async with AsyncClient(base_url=host, verify=False) as client:
        response = await client.post(
            url=f'/api/accounts/friendship-coef/?tg1={str(telegram_id_user)}&tg2={str(telegram_id_friend)}',
            headers=headers,
        )
        match response.status_code:
            case 404:
                raise UserNotFoundError()
            case 200:
                return int(response.json()['coef'])
            case _:
                raise UnknownError("Ой-ой...Что-то пошло не так 😰")


async def get_stars_accounts() -> list[StarProfile]:
    async with AsyncClient(base_url=host, verify=False) as client:
        response = await client.get(
            url='/api/accounts/?is_star=true',
            headers=headers
        )
        match response.status_code:
            case 200:
                return [
                    StarProfile(
                        name=d['name'],
                        gender=d['gender'],
                        photo=d['photo'],
                        id_tg=d['id_tg']
                    )
                    for d in response.json()
                ]
            case _:
                raise UnknownError("Ой-ой...Что-то пошло не так 😰")
