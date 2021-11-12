from datetime import datetime
from typing import List, Optional

from octoauth.architecture.encoders import BaseDTO
from octoauth.architecture.types import URL, Email, StringEnum


class SessionDTO(BaseDTO):
    uid: str
    account_uid: str
    expires_at: datetime
    issued_at: datetime
    ip_address: str
    country: Optional[str]
    city: Optional[str]
    browser: Optional[str]
    platform: Optional[str]


class GroupSummaryDTO(BaseDTO):
    uid: str
    name: str


class GroupDetailsDTO(GroupSummaryDTO):
    members: List["AccountSummaryDTO"]


class GroupCreateDTO(BaseDTO):
    name: str


class GroupUpdateDTO(BaseDTO):
    name: Optional[str]


class MemberRole(StringEnum):
    OWNER = "owner"
    MEMBER = "member"


class MembershipEditDTO(BaseDTO):
    nickname: str = None
    role: MemberRole = MemberRole.MEMBER


class AccountSummaryDTO(BaseDTO):
    uid: str
    username: str
    email: Email
    profile_url: Optional[URL]

    class Config:
        orm_mode = True


class AccountCreateDTO(BaseDTO):
    username: str
    email: Email
    password: str
    profile_url: Optional[URL]


class AccountUpdateDTO(BaseDTO):
    username: Optional[str]
    email: Optional[Email]
    password: Optional[str]
    profile_url: Optional[URL]


class AccountDetailsDTO(AccountSummaryDTO):
    groups: List["GroupSummaryDTO"]


GroupDetailsDTO.update_forward_refs()
