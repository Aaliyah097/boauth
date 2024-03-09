# t.me/regbo_bot
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils import get_start_params, verify_login, make_nonce, store_telegram_id
from api_requests import get_account, activate_account
from exceptions import UserNotFoundError

router = Router()


@router.message(Command("health"))
async def check_health(msg: Message):
    await msg.reply("OK")


@router.message(Command("start"))
async def start_handler(msg: Message, command: CommandObject):
    login, first_name, telegram_id = msg.from_user.username, msg.from_user.first_name, str(msg.from_user.id)
    redirect_uri = await get_start_params(command.args)

    if not login:
        await msg.answer("Пожалуйста, установите имя пользователя в настройках телеграм")
        return

    if not redirect_uri:
        await msg.answer("Не найден код для входа")
        return

    try:
        account = await get_account(verify_login(login))
    except UserNotFoundError:
        await msg.answer("Пользователь не найден")
        return

    if not account.is_active:
        try:
            await activate_account(account.pk, telegram_id)
        except UserNotFoundError:
            await msg.answer("Приглашение не найдено")
            return

    nonce = await store_telegram_id(make_nonce(), telegram_id)

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Вернуться в приложение", url=str(redirect_uri) + f"?nonce={nonce}")
    )

    await msg.answer(f"Привет, {first_name}!\n"
                     f"Вход выполнен успешно, нажми на кнопку ниже, чтобы вернуться в приложение: {msg.from_user.id}",
                     reply_markup=builder.as_markup())
