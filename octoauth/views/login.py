from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from octoauth.domain.accounts.authenticate import authentication_forbidden, authentication_required
from octoauth.domain.accounts.dtos import AccountSummaryDTO
from octoauth.domain.accounts.services import AccountService
from octoauth.exceptions import AuthenticationError
from octoauth.settings import SETTINGS

router = APIRouter()
templates = Jinja2Templates("octoauth/views/templates")


@router.get("/")
def home(
    request: Request,
    account_read_dto: AccountSummaryDTO = Depends(authentication_required),
):
    return templates.TemplateResponse("home.html", {"request": request, "username": account_read_dto.username})


@router.get("/login", dependencies=[Depends(authentication_forbidden)])
def display_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", dependencies=[Depends(authentication_forbidden)])
def handle_login_form_submit(
    request: Request,
    redirect: str = Query("/"),
    username: str = Form(...),
    password: str = Form(...),
):
    try:
        account_dto = AccountService.authenticate(username, password)
        session_id = AccountService.create_session(account_dto)
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    response = RedirectResponse(redirect, 303)
    response.set_cookie(
        "session_id",
        session_id,
        expires=int(SETTINGS.SESSION_COOKIE_LIFETIME.total_seconds()),
        httponly=True,
    )
    return response


@router.get("/logout")
def handle_login_form_submit(redirect: str = "/login"):
    response = RedirectResponse(redirect, 303)
    response.set_cookie(
        "session_id",
        "",
        expires=0,
        httponly=True,
    )
    return response
