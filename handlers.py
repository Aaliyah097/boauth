# t.me/regbo_bot
import aiogram.exceptions
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from utils import (
    get_start_params,
    get_signup_redirect_url,
    verify_login,
    make_nonce,
    store_telegram_id,
    is_valid_url
)
from api_requests import get_account, activate_account
from exceptions import UserNotFoundError
import vars


router = Router()


@router.message(Command("health"))
async def check_health(msg: Message):
    await msg.reply("OK")


@router.message(Command("start"))
async def start_handler(msg: Message, command: CommandObject):
    login, first_name, telegram_id = msg.from_user.username, msg.from_user.first_name, str(msg.from_user.id)

    if not login:
        await msg.answer(vars.LOGIN_NOT_FOUND_MESSAGE, parse_mode=ParseMode.HTML)
        return

    try:
        account = await get_account(verify_login(login))
        if not account.is_active:
            await activate_account(account.pk, telegram_id)
    except UserNotFoundError:
        account = None

    nonce = await store_telegram_id(make_nonce(), telegram_id)

    if not account:
        redirect_uri = await get_signup_redirect_url(command.args)
        message = vars.SIGNUP_REQUIRED % (str(first_name), str(nonce))
    else:
        redirect_uri = await get_start_params(command.args)
        message = vars.AUTH_SUCCESS % (str(first_name), str(nonce))

    if not redirect_uri:
        await msg.answer(vars.START_CODE_NOT_FOUND, parse_mode=ParseMode.HTML)
        return

    if is_valid_url(redirect_uri):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="Вернуться в приложение", url=str(redirect_uri))
        )
    else:
        builder = None

    await msg.answer(message,
                     reply_markup=builder.as_markup() if builder else None,
                     parse_mode=ParseMode.HTML)
