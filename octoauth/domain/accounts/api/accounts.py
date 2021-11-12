from typing import List

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from octoauth.architecture.query import Filters
from octoauth.architecture.security import AccountToken, account_token_required
from octoauth.domain.accounts.dtos import (
    AccountCreateDTO,
    AccountDetailsDTO,
    AccountSummaryDTO,
    AccountUpdateDTO,
)
from octoauth.domain.accounts.query import parse_accounts_query
from octoauth.domain.accounts.services import AccountService

router = APIRouter()


@router.get("/accounts", response_model=List[AccountSummaryDTO])
def search_accounts(filters: Filters = Depends(parse_accounts_query)):
    return AccountService.search(filters)


@router.get("/accounts/whoami", response_model=AccountDetailsDTO)
def get_my_account_details(token: AccountToken = Depends(account_token_required)):
    """
    Get current user's account details (authenticated by access token)
    """
    return AccountService.get_by_uid(token.account_uid)


@router.get("/accounts/{account_uid}", response_model=AccountDetailsDTO)
def get_account_details(account_uid: str, token: AccountToken = Depends(account_token_required)):
    if account_uid != token.account_uid and not token.is_admin:
        raise HTTPException(
            status_code=403, detail="You don't have permission to read this account's private information"
        )

    return AccountService.get_by_uid(account_uid)


@router.post("/accounts", status_code=201, response_model=AccountSummaryDTO)
def create_account(account_create_dto: AccountCreateDTO):
    return AccountService.create(account_create_dto)


@router.put("/accounts/{account_uid}", response_model=AccountSummaryDTO)
def edit_account(
    account_uid: str, account_update_dto: AccountUpdateDTO, token: AccountToken = Depends(account_token_required)
):
    if account_uid != token.account_uid and not token.is_admin:
        raise HTTPException(status_code=403, detail="You don't have permission to edit this account")

    return AccountService.update(account_uid, account_update_dto)


@router.delete("/accounts/{account_uid}", status_code=202)
def delete_account(account_uid: str, token: AccountToken = Depends(account_token_required)):
    if account_uid != token.account_uid and not token.is_admin:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this account")

    return AccountService.delete(account_uid)
