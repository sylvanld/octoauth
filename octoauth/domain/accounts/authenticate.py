from urllib.parse import quote_plus

from fastapi import Request
from fastapi.responses import RedirectResponse

from octoauth.domain.accounts.dtos import AccountSummaryDTO
from octoauth.domain.accounts.services import AccountService
from octoauth.exceptions import (
    AuthenticationError,
    AuthenticationForbidden,
    AuthenticationRequired,
)


def authentication_required(request: Request) -> AccountSummaryDTO:
    """
    Function to be injected as a dependency to ensure account authenticated and retrieve its data.

    Usage:
        @app.get("/account/me")
        def my_account_view(account_dto: AccountSummaryDTO = Depends(authentication_required)):
            ...
    """
    session_id = request.cookies.get("session_id")

    if session_id is None:
        raise AuthenticationRequired("Not authenticated. Missing session id")

    try:
        return AccountService.authenticate_from_session(session_id)
    except AuthenticationError as error:
        raise AuthenticationRequired("Error during session validation.") from error


def authentication_forbidden(request: Request):
    """
    Function to be injected as a dependency to ensure account is not authenticated to access an endpoint

    Usage:
        @app.get("/login", dependencies=[Depends(authentication_forbidden)])
    """
    try:
        authentication_required(request)
        raise AuthenticationForbidden("You cannot access this endpoint if already authenticated.")
    except AuthenticationRequired:
        return None


def authentication_required_exception_handler(request: Request, exc: AuthenticationRequired):
    """
    Handle AuthenticationRequired exceptions by redirecting to login page.
    """
    return RedirectResponse("/login?redirect=" + quote_plus(str(request.url)), 303)


def authentication_forbidden_exception_handler(request: Request, exc: AuthenticationForbidden):
    """
    If authentication is already provided, redirect.
    """
    redirect_uri = request.query_params.get("redirect", "/")
    return RedirectResponse(redirect_uri, 303)
