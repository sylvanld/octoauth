from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from octoauth.domain.accounts.dtos import AccountCreateDTO
from octoauth.domain.accounts.services import AccountService
from octoauth.settings import SETTINGS

router = APIRouter()
templates = Jinja2Templates("octoauth/views/templates")


@router.get("/register")
def display_registration_form(request: Request):
    return templates.TemplateResponse("register.html.j2", {"request": request})


@router.post("/register")
def handle_registration_form(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_url: str = Form(None),
):
    AccountService.create(AccountCreateDTO(username=username, email=email, profile_url=profile_url, password=password))

    if not SETTINGS.MAILING_ENABLED:
        return RedirectResponse("/login")
    return templates.TemplateResponse("validation-required.html", {"request": request})
