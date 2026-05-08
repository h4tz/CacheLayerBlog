"""Ninja routes for /auth/."""

from __future__ import annotations

from ninja import Router

from schemas.users import LoginIn, RegisterIn, TokenPairOut, UserOut
from services.auth_service import AuthService

from ..auth import JWTAuth

router = Router(tags=["auth"])


@router.post("/register", response={201: UserOut})
def register(request, payload: RegisterIn):
    user = AuthService().register(
        email=payload.email, username=payload.username, password=payload.password
    )
    return 201, UserOut(id=user.id, email=user.email, username=user.username, role=user.role)


@router.post("/login", response=TokenPairOut)
def login(request, payload: LoginIn):
    tokens = AuthService().login(email=payload.email, password=payload.password)
    return TokenPairOut(**tokens.to_dict())


@router.get("/me", response=UserOut, auth=JWTAuth())
def me(request):
    user = request.user
    return UserOut(id=user.id, email=user.email, username=user.username, role=user.role)
