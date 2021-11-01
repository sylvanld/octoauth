from fastapi import APIRouter

from octoauth.domain.oauth2.dtos import ScopeDTO
from octoauth.domain.oauth2.services import ScopeService

router = APIRouter()


@router.post("/scopes", response_model=ScopeDTO)
def create_scope(scope_create_dto: ScopeDTO):
    return ScopeService.create(scope_create_dto)
