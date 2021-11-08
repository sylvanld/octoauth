from dataclasses import dataclass
from typing import List, Optional

from octoauth.architecture.encoders import BaseDTO
from octoauth.architecture.types import URL, StringEnum


class ApplicationReadDTO(BaseDTO):
    uid: str
    name: str
    description: str
    client_id: str
    icon_uri: str = None


class ApplicationReadOnceDTO(ApplicationReadDTO):
    client_secret: str


class ApplicationCreateDTO(BaseDTO):
    name: str
    description: str
    client_id: str
    icon_uri: str = None


class ApplicationUpdateDTO(BaseDTO):
    # client_id can't be modified once set
    name: str = None
    description: str = None
    icon_uri: str = None


class RedirectURIEditDTO(BaseDTO):
    redirect_uri: str


class RedirectURIReadDTO(BaseDTO):
    uid: str
    redirect_uri: str


class TokenGrantDTO(BaseDTO):
    access_token: str
    refresh_token: Optional[str]
    expires: int
    token_type: str
    scopes: List[str] = []


class ScopeDTO(BaseDTO):
    code: str
    description: str


# get token requests related dtos
class GrantType(StringEnum):
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"


@dataclass
class BaseTokenRequestDTO:
    client_id: str
    client_secret: Optional[str]


@dataclass
class TokenRequestWithImplicitGrantsDTO:
    account_uid: str
    client_id: str
    redirect_uri: str
    scope: str


@dataclass
class TokenRequestWithAuthorizationCodeDTO(BaseTokenRequestDTO):
    scope: Optional[str]
    code: str
    redirect_uri: URL
    code_verifier: str
    grant_type = "authorization_code"


@dataclass
class TokenRequestWithClientCredentialsDTO(BaseTokenRequestDTO):
    scope: Optional[str]
    grant_type = "client_credentials"


@dataclass
class TokenRequestWithRefreshTokenDTO(BaseTokenRequestDTO):
    refresh_token: str
    scope: Optional[str]
    grant_type = "refresh_token"


@dataclass
class TokenRequestDTO:
    client_id: str
    client_secret: str = None
    code: str = None
    scope: str = None
    redirect_uri: URL = None
    code_verifier: str = None
    refresh_token: str = None
    grant_type: str = None


# authorization related dtos
class ChallengeMethod(StringEnum):
    RS256 = "RS256"


class ResponseType(StringEnum):
    TOKEN = "token"
    CODE = "code"


@dataclass
class AuthorizeQueryParams:
    client_id: str
    scope: str
    redirect_uri: str
    response_type: ResponseType
    state: str = None
    code_challenge: str = None
    code_challenge_method: ChallengeMethod = None
