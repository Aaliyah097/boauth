# t.me/regbo_bot
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from utils import get_start_params, verify_login, make_nonce, store_telegram_id
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
    redirect_uri = await get_start_params(command.args)

    if not login:
        await msg.answer(vars.LOGIN_NOT_FOUND_MESSAGE, parse_mode=ParseMode.HTML)
        return

    if not redirect_uri:
        await msg.answer(vars.START_CODE_NOT_FOUND, parse_mode=ParseMode.HTML)
        return

    try:
        account = await get_account(verify_login(login))
    except UserNotFoundError:
        await msg.answer(vars.USER_NOT_FOUND, parse_mode=ParseMode.HTML)
        return

    if not account.is_active:
        try:
            await activate_account(account.pk, telegram_id)
        except UserNotFoundError:
            await msg.answer(vars.USER_NOT_FOUND, parse_mode=ParseMode.HTML)
            return

    nonce = await store_telegram_id(make_nonce(), telegram_id)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Вернуться в приложение", url=str(redirect_uri) + f"?nonce={nonce}")
    )

    await msg.answer(vars.AUTH_SUCCESS % (first_name, nonce),
                     reply_markup=builder.as_markup(),
                     parse_mode=ParseMode.HTML)
