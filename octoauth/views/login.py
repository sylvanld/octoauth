from typing import Optional

from fastapi import APIRouter, Depends, Form, Header, Query, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from octoauth.domain.accounts.authenticate import (
    authentication_forbidden,
    authentication_required,
)
from octoauth.domain.accounts.services import AccountService
from octoauth.exceptions import AuthenticationError
from octoauth.settings import SETTINGS

router = APIRouter()
templates = Jinja2Templates("octoauth/views/templates")


@router.get("/", dependencies=[Depends(authentication_required)])
def dashboard():
    return RedirectResponse(SETTINGS.DASHBOARD_URL, 303)


@router.get("/login", dependencies=[Depends(authentication_forbidden)])
def display_login_form(request: Request):
    return templates.TemplateResponse("login.html.j2", {"request": request})


@router.post("/login", dependencies=[Depends(authentication_forbidden)])
def handle_login_form_submit(
    request: Request,
    redirect: str = Query("/"),
    username: str = Form(...),
    password: str = Form(...),
    platform: str = Form(None),
    browser: str = Form(None),
    x_real_ip: Optional[str] = Header(None),
):
    try:
        ip_address = request.client[0] or x_real_ip
        account_dto = AccountService.authenticate(username, password)
        session_id = AccountService.create_session(account_dto, ip_address, platform, browser)
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from error

    response = RedirectResponse(redirect, 303)
    response.set_cookie(
        "session_id",
        session_id,
        expires=int(SETTINGS.SESSION_COOKIE_LIFETIME.total_seconds()),
        httponly=True,
    )
    return response


@router.get("/logout")
def handle_login_form_submit(request: Request, redirect: str = "/login"):
    session_uid = request.cookies.get("session_id")
    if session_uid:
        AccountService.revoke_session(session_uid)
    # once session is revoked, redirect to login page and clear cookie
    response = RedirectResponse(redirect, 303)
    response.set_cookie(
        "session_id",
        "",
        expires=0,
        httponly=True,
    )
    return response
