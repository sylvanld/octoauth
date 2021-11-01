from datetime import datetime
from typing import List

from octoauth.architecture.database import use_database
from octoauth.architecture.query import Filters
from octoauth.domain.oauth2.database import Application, AuthorizationCode, Scope
from octoauth.settings import SETTINGS

from .dtos import (
    ApplicationCreateDTO,
    ApplicationReadDTO,
    ApplicationUpdateDTO,
    ScopeDTO,
    TokenRequestWithAuthorizationCodeDTO,
    TokenRequestWithClientCredentialsDTO,
    TokenRequestWithRefreshTokenDTO,
)


class ApplicationService:
    @classmethod
    def find_one(cls, **filters):
        """
        Get an oauth2 client application details.
        """
        application = Application.find_one(**filters)
        return ApplicationReadDTO.from_orm(application)

    @classmethod
    @use_database
    def search(cls, filters: Filters) -> List[ApplicationReadDTO]:
        """
        Get a list of oauth2 client applications matching the filters.
        """
        applications: List[Application] = Application.query.filter(*filters).all()
        return [ApplicationReadDTO.from_orm(application) for application in applications]

    @classmethod
    @use_database
    def create(cls, application_create: ApplicationCreateDTO) -> ApplicationReadDTO:
        """
        Declare an oauth2 client application.
        """
        application = Application.create(**application_create.dict())
        return ApplicationReadDTO.from_orm(application)

    @classmethod
    @use_database
    def update(cls, application_uid: str, application_update: ApplicationUpdateDTO) -> ApplicationReadDTO:
        """
        Update an oauth2 client application details.
        """
        application = Application.get_by_uid(application_uid)
        application.update(**application_update.dict())
        return ApplicationReadDTO.from_orm(application)

    @classmethod
    @use_database
    def delete(cls, application_uid: str) -> ApplicationReadDTO:
        """
        Delete an oauth2 client application details.
        """
        application = Application.get_by_uid(application_uid)
        application.delete()


class ScopeService:
    @staticmethod
    @use_database
    def create(scope_dto: ScopeDTO):
        scope = Scope.create(**scope_dto.dict())
        return ScopeDTO.from_orm(scope)

    @staticmethod
    @use_database
    def get_scopes_from_string(scope: str):
        if not scope:
            raise ValueError("ScopeService.get_scopes_from_string can't parse empty scope")

        # scope is for example: account:read,account:write
        scope_codes = set(scope.split(","))
        scopes = Scope.query.filter(Scope.code.in_(scope_codes)).all()

        if len(scopes) != len(scope_codes):
            existing_codes = set((scope.code for scope in scopes))
            missing_codes = scope_codes.difference(existing_codes)
            raise ValueError(f"The following scopes does not exists {', '.join(missing_codes)}")

        return [ScopeDTO.from_orm(scope) for scope in scopes]


class AuthorizationService:
    @classmethod
    @use_database
    def generate_authorization_code(
        cls,
        account_uid: str,
        client_id: str,
        scope: str,
        code_challenge: str = None,
        code_challenge_method: str = None,
    ) -> str:
        """
        Generate an authorization code, store it in database and returns its value.
        """
        if (code_challenge and code_challenge_method is None) or (code_challenge_method and code_challenge is None):
            raise ValueError(
                "In order to use PKCE, you must provide both 'code_challenge' and 'code_challenge_method' parameters"
            )

        authorization_code = AuthorizationCode.create(
            expires=datetime.utcnow() + SETTINGS.AUTHORIZATION_CODE_EXPIRES,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            grants=[],
        )

        return authorization_code.code

    @classmethod
    @use_database
    def validate_authorization_code(cls, code: str):
        """
        Ensure that an authorization code is valid.
        """
        # start by removing outdated codes to avoid matching it
        AuthorizationCode.delete_all(AuthorizationCode.expires <= datetime.utcnow())
        # will fail if authorization code does not exists
        authorization_code = AuthorizationCode.find_one(code=code)
        # once found, delete code so it can't be used twice
        authorization_code.delete()


class TokenService:
    @staticmethod
    def generate_token_from_authorization_code(request: TokenRequestWithAuthorizationCodeDTO):
        ...

    @staticmethod
    def generate_token_from_client_credentials(request: TokenRequestWithClientCredentialsDTO):
        ...

    @staticmethod
    def generate_token_from_refresh_token(request: TokenRequestWithRefreshTokenDTO):
        ...
