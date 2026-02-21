"""Auth routes - token endpoint."""
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt import Token, login_for_access_token

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Obtain JWT access token. Use username/password form data."""
    return await login_for_access_token(form_data)
