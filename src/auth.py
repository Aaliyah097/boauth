import json
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.dispatcher.flags import get_flag
from src.api_requests import (
    get_account,
    signup_user
)
from src import vars
from src import buttons
from src import models
from src.utils import (
    verify_login,
    make_nonce,
    store_telegram_id,
)
from src import exceptions
from src.cache import RedisConnector
from src.exceptions import UnknownError


class AuthorizationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        authorization = get_flag(data, "signup_confirm_required")
        if authorization is None:
            return await handler(event, data)

        username, telegram_id = event.chat.username, event.chat.id
        if not username:
            return await event.answer(
                text=vars.LOGIN_NOT_FOUND_MESSAGE,
                reply_markup=buttons.Menu(
                    telegram_id).as_markup(resize_keyboard=True)
            )

        username = str(verify_login(username))

        try:
            account = await get_account(verify_login(username))
        except exceptions.UserNotFoundError:
            account = await signup_user(username, telegram_id)
        except UnknownError as e:
            return await event.answer(str(e))

        if len(str(event.text).split(" ")) > 1:
            return await handler(event, data)

        if not account.partial_signup:
            builder = ReplyKeyboardBuilder()
            builder.row(buttons.SignupFinishButton(await store_telegram_id(make_nonce(6), telegram_id)))
            return await event.answer(
                vars.ONBOARDING_REQUIRED,
                reply_markup=builder.as_markup(resize_keyboard=True),
            )

        return await handler(event, data)
