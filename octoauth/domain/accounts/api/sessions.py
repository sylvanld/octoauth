from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from octoauth.architecture.security import AccountToken, account_token_required
from octoauth.domain.accounts.services import AccountService

router = APIRouter()


@router.get("/sessions")
def get_account_sessions(token: AccountToken = Depends(account_token_required)):
    return AccountService.get_sessions(token.account_uid)


@router.post("/sessions/{session_uid}/revoke", status_code=202)
def revoke_account_session(session_uid, token: AccountToken = Depends(account_token_required)):
    session = AccountService.get_session(session_uid)
    if session.account_uid != token.account_uid and not token.is_admin:
        raise HTTPException(
            status_code=403, detail=f"You are not allowed to revoke sessions for account {session.account_uid}"
        )

    return AccountService.revoke_session(session_uid)
