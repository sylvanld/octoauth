from typing import Optional

from fastapi import APIRouter, Form

from octoauth.domain.oauth2.dtos import GrantType, TokenGrantDTO, TokenRequestDTO
from octoauth.domain.oauth2.parsers import TokenRequestParser
from octoauth.domain.oauth2.services import TokenService
from octoauth.exceptions import UIException

router = APIRouter()


@router.post("/token", response_model=TokenGrantDTO)
def get_token(
    grant_type: GrantType = Form(
        ...,
        description="**Always mandatory**. Indicates which authorization flow is used to get an access token",
    ),
    client_id: str = Form(
        None,
        description="**Mandatory in 'authorization_code' flow if basic auth is not passed**. IE suitable for used case where public client use code flow with PKCE.",
    ),
    scope: Optional[str] = Form(
        None,
        description="**Only suitable for refresh_token and authorization_code flows**. May be used to restrict scope compared to the one granted originally.",
    ),
    code: str = Form(
        None,
        description='**Must be set if using "authorization_code" flow**. Code obtained while calling /authorize endpoint with response_type "code"',
    ),
    refresh_token: Optional[str] = Form(
        None,
        description="**Only suitable for refresh_token flow**. Value of the refresh token issued previously.",
    ),
    code_verifier: Optional[str] = Form(
        None,
        description='**Suitable for "authorization_code" flow only. Must be set if using PKCE** (i.e if you called /authorize endpoint with a "code_challenge")',
    ),  # code verifier is mendatory only if code challenge was supplied at authorization
    redirect_uri: Optional[str] = Form(
        None,
        description='**Suitable for "authorization_code" flow only**. Must be the same redirect_uri as the one used to retrieve authorization code',
    ),
):
    request_dto = TokenRequestDTO(
        grant_type=grant_type,
        client_id=client_id,
        scope=scope,
        code=code,
        refresh_token=refresh_token,
        code_verifier=code_verifier,
        redirect_uri=redirect_uri,
    )

    if grant_type == GrantType.AUTHORIZATION_CODE:
        request_with_code = TokenRequestParser.parse_authorization_code(request_dto)
        token_grant = TokenService.generate_token_from_authorization_code(request_with_code)
    elif grant_type == GrantType.CLIENT_CREDENTIALS:
        request_with_client_credentials = TokenRequestParser.parse_client_credentials(request_dto)
        token_grant = TokenService.generate_token_from_client_credentials(request_with_client_credentials)
    elif grant_type == GrantType.REFRESH_TOKEN:
        request_with_refresh_token = TokenRequestParser.parse_refresh_token(request_dto)
        token_grant = TokenService.generate_token_from_refresh_token(request_with_refresh_token)
    else:
        raise UIException(
            message=f"Unsupported value for parameter 'grant_type': {grant_type}",
            details="Supported values: token, code",
        )

    return token_grant
