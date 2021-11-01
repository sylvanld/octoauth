from typing import List

from fastapi import APIRouter

from octoauth.domain.accounts.dtos import (
    GroupCreateDTO,
    GroupDetailsDTO,
    GroupSummaryDTO,
    GroupUpdateDTO,
    MembershipEditDTO,
)
from octoauth.domain.accounts.services import GroupService

router = APIRouter()


@router.get("/groups", response_model=List[GroupSummaryDTO])
def search_groups():
    return GroupService.search()


@router.get("/groups/{group_uid}", response_model=GroupDetailsDTO)
def get_group_details(group_uid: str):
    return GroupService.get_by_uid(group_uid)


@router.post("/groups", response_model=GroupSummaryDTO, status_code=201)
def create_group(group_create_dto: GroupCreateDTO):
    """
    Create a group that will belongs to current user (authenticated by token)
    """
    return GroupService.create("42", group_create_dto)


@router.put("/groups/{group_uid}", response_model=GroupSummaryDTO)
def edit_group(group_uid: str, group_update_dto: GroupUpdateDTO):
    """
    Update a group's information
    """
    return GroupService.update(group_uid, group_update_dto)


@router.delete("/groups/{group_uid}", status_code=202)
def disolve_group(group_uid: str):
    """
    Remove all members of a group, then delete this group.
    Be carefull as deleted groups can not be restored.
    """
    return GroupService.delete(group_uid)


@router.put("/groups/{group_uid}/members/{account_uid}")
def add_or_update_group_member(group_uid: str, account_uid: str, membership_dto: MembershipEditDTO):
    """
    Edit role/nickname for a member of a group. If account is not member of this group, add it as a member.
    This endpoint is restricted to group owners.
    """
    return GroupService.add_member(group_uid, account_uid)


@router.delete("/groups/{group_uid}/members/{account_uid}")
def remove_member_from_group(group_uid: str, account_uid: str):
    """
    Delete member from a group. This endpoint is restricted to group owners or concerned member itself.
    """
    return GroupService.remove_member(group_uid, account_uid)
