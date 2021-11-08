from fastapi import APIRouter

from octoauth.domain.accounts.services import AccountService

router = APIRouter()


@router.get("/sessions")
def get_account_sessions():
    account_uid = AccountService.search([])[0].uid
    return AccountService.get_sessions(account_uid)


@router.post("/sessions/{session_uid}/revoke", status_code=202)
def revoke_account_session(session_uid):
    return AccountService.revoke_session(session_uid)
