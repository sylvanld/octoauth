from typing import List
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from octoauth.domain.accounts.authenticate import (
    AccountSummaryDTO,
    authentication_required,
)
from octoauth.domain.oauth2.dtos import ResponseType, TokenRequestWithImplicitGrantsDTO
from octoauth.domain.oauth2.parsers import (
    AuthorizeQueryParams,
    parse_authorization_params,
)
from octoauth.domain.oauth2.services import (
    ApplicationService,
    AuthorizationService,
    ScopeService,
    TokenService,
)

router = APIRouter()
templates = Jinja2Templates("octoauth/views/templates")


@router.get("/authorize")
def display_authorization_form(
    request: Request,
    authorization_params: AuthorizeQueryParams = Depends(parse_authorization_params),
    account_dto: AccountSummaryDTO = Depends(authentication_required),
    show_consent_dialog: bool = Query(
        False,
        description="Boolean value that indicates whether consent dialog should be displayed even if permission has already been granted.",
    ),
):
    try:
        application_dto = ApplicationService.find_one(client_id=authorization_params.client_id)
    except:
        raise HTTPException(400, "No client application registered named: %s" % authorization_params.client_id)

    try:
        scopes = ScopeService.get_scopes_from_string(authorization_params.scope)
    except ValueError as error:
        raise HTTPException(400, str(error))

    if not show_consent_dialog:
        required_scopes = set([scope.code for scope in scopes])
        already_granted_scopes = ScopeService.get_client_granted_scopes(
            account_dto.uid, authorization_params.client_id
        )

        # submit without displaying login screen if authorization have been granted previously
        if required_scopes.issubset(already_granted_scopes):
            return submit_authorization_form(
                scopes=required_scopes, authorization_params=authorization_params, account_dto=account_dto
            )

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
    scopes: List[str] = Form(...),
    authorization_params: AuthorizeQueryParams = Depends(parse_authorization_params),
    account_dto: AccountSummaryDTO = Depends(authentication_required),
):
    response_data = {}
    if authorization_params.state:
        response_data["state"] = authorization_params.state

    if authorization_params.response_type == ResponseType.CODE:
        authorization_code = AuthorizationService.generate_authorization_code(
            account_uid=account_dto.uid,
            client_id=authorization_params.client_id,
            scopes=scopes,
            code_challenge=authorization_params.code_challenge,
            code_challenge_method=authorization_params.code_challenge_method,
        )
        response_data["code"] = authorization_code
        response = RedirectResponse(
            authorization_params.redirect_uri + "?" + urlencode(response_data), status.HTTP_303_SEE_OTHER
        )
    elif authorization_params.response_type == ResponseType.TOKEN:
        grant_data = TokenService.generate_token_from_implicit_grant(
            TokenRequestWithImplicitGrantsDTO(
                account_uid=account_dto.uid,
                client_id=authorization_params.client_id,
                scope=authorization_params.scope,
                redirect_uri=authorization_params.redirect_uri,
            )
        )
        return RedirectResponse(
            authorization_params.redirect_uri + "#" + urlencode(grant_data.dict()), status.HTTP_303_SEE_OTHER
        )
    else:
        raise ValueError(f"Unsupported response type: {authorization_params.response_type}")

    return response
