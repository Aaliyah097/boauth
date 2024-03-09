import pytest
from api_requests import get_account, activate_account
from models import Account
from exceptions import UserNotFoundError


@pytest.mark.asyncio
async def test_get_account():
    result = await get_account("@thedawnofmydeath")
    assert isinstance(result, Account)
    try:
        result = await get_account("@randomname")
    except UserNotFoundError:
        assert True
    else:
        assert False


@pytest.mark.asyncio
async def test_account_activate():
    await activate_account(2, "1")
    try:
        await activate_account(20, "1")
    except UserNotFoundError:
        assert True
    else:
        assert False
