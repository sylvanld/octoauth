from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import octoauth.domain.accounts.api
import octoauth.domain.oauth2.api
import octoauth.views
from octoauth.domain.accounts.authenticate import (
    authentication_forbidden_exception_handler,
    authentication_required_exception_handler,
)
from octoauth.exceptions import AuthenticationForbidden, AuthenticationRequired
from octoauth.settings import SETTINGS


class OctoAuthASGI(FastAPI):
    def __init__(self):
        super().__init__(
            title=SETTINGS.API_TITLE,
            description=SETTINGS.API_DESCRIPTION,
            version=SETTINGS.API_VERSION,
            openapi_tags=SETTINGS.API_TAGS_METADATA,
            docs_url="/api",
        )
        self.register_domains()
        self.register_middlewares()
        self.register_error_handlers()

    def register_domains(self):
        self.include_router(octoauth.domain.accounts.api.router)
        self.include_router(octoauth.domain.oauth2.api.router)
        self.include_router(octoauth.views.app)

    def register_middlewares(self):
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def register_error_handlers(self):
        self.exception_handler(AuthenticationRequired)(authentication_required_exception_handler)
        self.exception_handler(AuthenticationForbidden)(authentication_forbidden_exception_handler)
