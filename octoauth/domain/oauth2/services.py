from datetime import datetime
from typing import Iterable, List, Set

from octoauth.architecture.database import use_database
from octoauth.architecture.query import Filters
from octoauth.architecture.security import generate_access_token
from octoauth.domain.oauth2.database import Application, AuthorizationCode, AuthorizedRedirectURI, Grant, Scope
from octoauth.settings import SETTINGS

from .dtos import (
    ApplicationCreateDTO,
    ApplicationReadDTO,
    ApplicationReadOnceDTO,
    ApplicationUpdateDTO,
    RedirectURIEditDTO,
    RedirectURIReadDTO,
    ScopeDTO,
    TokenGrantDTO,
    TokenRequestWithAuthorizationCodeDTO,
    TokenRequestWithClientCredentialsDTO,
    TokenRequestWithImplicitGrantsDTO,
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
        return ApplicationReadOnceDTO.from_orm(application)

    @classmethod
    @use_database
    def update(cls, application_uid: str, application_update: ApplicationUpdateDTO) -> ApplicationReadDTO:
        """
        Update an oauth2 client application details.
        """
        application = Application.get_by_uid(application_uid)
        application.update(**application_update.dict())
        return ApplicationReadOnceDTO.from_orm(application)

    @classmethod
    @use_database
    def delete(cls, application_uid: str) -> ApplicationReadDTO:
        """
        Delete an oauth2 client application details.
        """
        application = Application.get_by_uid(application_uid)
        application.delete()

    @staticmethod
    @use_database
    def get_authorized_redirect_uris(application_uid: str) -> List[RedirectURIReadDTO]:
        authorized_uris = AuthorizedRedirectURI.query.filter_by(application_uid=application_uid).all()
        return [RedirectURIReadDTO.from_orm(authorized_uri) for authorized_uri in authorized_uris]

    @staticmethod
    @use_database
    def add_authorized_redirect_uri(application_uid, redirect_uri_edit_dto: RedirectURIEditDTO) -> RedirectURIReadDTO:
        instance = AuthorizedRedirectURI.create(application_uid=application_uid, redirect_uri=redirect_uri_edit_dto.redirect_uri)
        return RedirectURIReadDTO.from_orm(instance)

    @staticmethod
    @use_database
    def update_authorized_redirect_uri(application_uid, redirect_uri_uid, redirect_uri_edit_dto: RedirectURIEditDTO) -> RedirectURIReadDTO:
        instance = AuthorizedRedirectURI.find_one(uid=redirect_uri_uid, application_uid=application_uid)
        instance.update(redirect_uri=redirect_uri_edit_dto.redirect_uri)
        return RedirectURIReadDTO.from_orm(instance)
    
    @staticmethod
    @use_database
    def remove_authorized_redirect_uri(application_uid, redirect_uri_uid):
        instance = AuthorizedRedirectURI.find_one(uid = redirect_uri_uid, application_uid = application_uid)
        instance.delete()


class ScopeService:
    @staticmethod
    @use_database
    def create(scope_dto: ScopeDTO):
        scope = Scope.create(**scope_dto.dict())
        return ScopeDTO.from_orm(scope)

    @staticmethod
    @use_database
    def get_scopes_from_string(scope: str) -> List[ScopeDTO]:
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

    @staticmethod
    @use_database
    def get_client_granted_scopes(account_uid: str, client_id: str) -> Set[ScopeDTO]:
        """
        Retrieve the list of scopes granted to a client
        """
        grants: List[Grant] = Grant.query.filter_by(account_uid=account_uid, client_id=client_id).all()
        return set([grant.scope_code for grant in grants])

    @classmethod
    @use_database
    def add_client_granted_scopes(cls, account_uid: str, client_id: str, scopes: List[str]) -> Set[ScopeDTO]:
        old_granted_scopes = cls.get_client_granted_scopes(account_uid, client_id)
        new_granted_scopes = set([scope_code for scope_code in scopes])

        # create missing client grant
        for scope_code in new_granted_scopes.difference(old_granted_scopes):
            Grant.create(
                account_uid=account_uid,
                client_id=client_id,
                scope_code=scope_code
            )

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

        if not scope:
            raise ValueError("Scope argument is mandatory to generate client_id")

        ScopeService.add_client_granted_scopes(account_uid, client_id, scope.split(','))

        application_grants = Grant.query.filter(
            Grant.account_uid == account_uid,
            Grant.client_id == client_id,
            Grant.scope_code.in_(scope.split(','))
        ).all()

        authorization_code = AuthorizationCode.create(
            expires=datetime.utcnow() + SETTINGS.AUTHORIZATION_CODE_EXPIRES,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            grants=application_grants,
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
    def generate_token_from_implicit_grant(request: TokenRequestWithImplicitGrantsDTO):
        expires = datetime.utcnow() + SETTINGS.ACCESS_TOKEN_EXPIRES
        return TokenGrantDTO(
            access_token=generate_access_token(account_uid=request.account_uid, client_id=request.client_id, expires=SETTINGS.ACCESS_TOKEN_EXPIRES, scope=request.scope),
            expires=expires.timestamp(),
            token_type="Bearer"
        )
    
    @staticmethod
    def generate_token_from_authorization_code(request: TokenRequestWithAuthorizationCodeDTO):
        ...

    @staticmethod
    def generate_token_from_client_credentials(request: TokenRequestWithClientCredentialsDTO):
        ...

    @staticmethod
    def generate_token_from_refresh_token(request: TokenRequestWithRefreshTokenDTO):
        ...
