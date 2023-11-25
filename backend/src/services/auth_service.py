from datetime import timedelta

from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.config import settings
from src.models.users import Users
from src.schemas.users import TokenResponse
from src.security import create_access_token, create_refresh_token, get_token_payload, verify_password
from src.utils.unitofwork import IUnitOfWork


async def get_token(uow: IUnitOfWork, data: OAuth2PasswordRequestForm):
    async with uow:
        user = await uow.users.find_one(username=data.username)

        if not user:
            raise HTTPException(
                status_code=400,
                detail="User is not registered with us.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Invalid Login Credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await _get_user_token(user=user)


async def get_refresh_token(uow: IUnitOfWork, token):
    payload = get_token_payload(token=token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: int = payload.get("id")
    async with uow:
        user = await uow.users.find_one(id=user_id)
        return await _get_user_token(user=user, refresh_token=token)


async def _get_user_token(user: Users, refresh_token=None):
    payload = {"id": user.id}

    access_token_expire = timedelta(minutes=settings.access_token_expire)

    access_token = await create_access_token(payload, access_token_expire)
    if not refresh_token:
        refresh_token_expire = timedelta(minutes=settings.refresh_token_expire)
        refresh_token = await create_refresh_token(payload, refresh_token_expire)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=access_token_expire.seconds)
