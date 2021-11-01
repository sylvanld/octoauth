from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from octoauth.domain.accounts.authenticate import AccountSummaryDTO, authentication_required
from octoauth.domain.oauth2.parsers import AuthorizeQueryParams, parse_authorization_params
from octoauth.domain.oauth2.services import ApplicationService, AuthorizationService, ScopeService

router = APIRouter()
templates = Jinja2Templates("octoauth/views/templates")


@router.get("/authorize")
def display_authorization_form(
    request: Request,
    authorization_params: AuthorizeQueryParams = Depends(parse_authorization_params),
    account_dto: AccountSummaryDTO = Depends(authentication_required),
):
    application_dto = ApplicationService.find_one(client_id=authorization_params.client_id)
    scopes = ScopeService.get_scopes_from_string(authorization_params.scope)
    return templates.TemplateResponse(
        "authorize.html",
        {
            "request": request,
            "account": account_dto,
            "application": application_dto,
            "scopes": scopes,
        },
    )


@router.post("/authorize")
def submit_authorization_form(
    authorization_params: AuthorizeQueryParams = Depends(parse_authorization_params),
    account_dto: AccountSummaryDTO = Depends(authentication_required),
):
    authorization_code = AuthorizationService.generate_authorization_code(
        account_uid=account_dto.uid,
        client_id=authorization_params.client_id,
        scope=authorization_params.scope,
        code_challenge=authorization_params.code_challenge,
        code_challenge_method=authorization_params.code_challenge_method,
    )
    # response = RedirectResponse(authorization_params.redirect_uri, status.HTTP_303_SEE_OTHER)
    return response
