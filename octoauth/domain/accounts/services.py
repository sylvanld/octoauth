from datetime import datetime
from typing import List

from octoauth.architecture.database import use_database
from octoauth.architecture.events import publish_event
from octoauth.architecture.query import Filters
from octoauth.architecture.security import get_ip_info, hash_password, verify_password
from octoauth.exceptions import AuthenticationError
from octoauth.settings import SETTINGS

from .database import Account, Group, SessionCookie
from .dtos import (
    AccountCreateDTO,
    AccountDetailsDTO,
    AccountSummaryDTO,
    AccountUpdateDTO,
    GroupCreateDTO,
    GroupDetailsDTO,
    GroupSummaryDTO,
    GroupUpdateDTO,
    SessionDTO,
)
from .events import ACCOUNT_CREATED, ACCOUNT_DELETED


class AccountService:
    @staticmethod
    @use_database
    def get_by_uid(account_uid: str) -> AccountDetailsDTO:
        account = Account.get_by_uid(account_uid)
        return AccountDetailsDTO.from_orm(account)

    @staticmethod
    @use_database
    def search(filters: Filters):
        accounts = Account.query.filter(*filters).all()
        return [AccountSummaryDTO.from_orm(account) for account in accounts]

    @staticmethod
    @use_database
    @publish_event(ACCOUNT_CREATED)
    def create(account_create_dto: AccountCreateDTO) -> AccountSummaryDTO:
        account_data = account_create_dto.dict()

        # hash password
        password = account_data.pop("password")
        account_data["password_hash"] = hash_password(password)

        account = Account.create(**account_data)
        return AccountSummaryDTO.from_orm(account)

    @staticmethod
    @use_database
    def authenticate(username: str, password: str) -> AccountSummaryDTO:
        """
        Ensure couple (username, password) matches a valid account in database.

        raises:
            AuthenticationError
        """
        account: Account = Account.query.filter_by(username=username).first()
        if account is None or not verify_password(password, account.password_hash):
            raise AuthenticationError("Authentication failed. Wrong credentials.")
        return AccountSummaryDTO.from_orm(account)

    @staticmethod
    @use_database
    def authenticate_from_session(session_id):
        # prune outdated sessions
        SessionCookie.query.filter(SessionCookie.expires_at < datetime.utcnow()).delete()

        # get first session
        session: SessionCookie = SessionCookie.query.filter_by(uid=session_id).first()
        if session is None:
            raise AuthenticationError("Authentication failed. Session ID not found in database.")

        # find account matching this session
        account = Account.query.filter_by(uid=session.account_uid).first()
        if account is None:
            raise AuthenticationError("Authentication failed. Can't find account associated with this session.")

        return AccountSummaryDTO.from_orm(account)

    @staticmethod
    @use_database
    def create_session(
        account_dto: AccountSummaryDTO, ip_address: str = None, platform: str = None, browser: str = None
    ) -> str:
        """
        Create a session and returns its UID
        """
        # abort ip address info if not IPV4 address
        ip_info = {}
        if ip_address and len(ip_address) < 15:
            ip_info = get_ip_info(ip_address)

        session = SessionCookie.create(
            account_uid=account_dto.uid,
            ip_address=ip_info.get("ip"),
            country=ip_info.get("country"),
            city=ip_info.get("city"),
            platform=platform,
            browser=browser,
            expires_at=datetime.utcnow() + SETTINGS.SESSION_COOKIE_LIFETIME,
        )

        return session.uid

    @staticmethod
    @use_database
    def get_sessions(account_uid) -> List[SessionCookie]:
        session_cookies = SessionCookie.query.filter_by(account_uid=account_uid).all()
        return [SessionDTO.from_orm(session_cookie) for session_cookie in session_cookies]

    @staticmethod
    @use_database
    def revoke_session(session_uid):
        session = SessionCookie.get_by_uid(session_uid)
        session.delete()

    @staticmethod
    @use_database
    def update(account_uid: str, account_update_dto: AccountUpdateDTO) -> AccountSummaryDTO:
        account_data = account_update_dto.dict()

        # hash password if needed
        password = account_data.pop("password", None)
        if password is not None:
            account_data["password_hash"] = hash_password(password)

        account = Account.get_by_uid(account_uid)
        account.update(**account_data)
        return AccountSummaryDTO.from_orm(account)

    @staticmethod
    @use_database
    @publish_event(ACCOUNT_DELETED)
    def delete(account_uid: int):
        account = Account.get_by_uid(account_uid)
        account_dto = AccountSummaryDTO.from_orm(account)
        account.delete()
        return account_dto


class GroupService:
    @staticmethod
    @use_database
    def get_by_uid(group_uid: str) -> GroupDetailsDTO:
        group = Group.get_by_uid(group_uid)
        return GroupDetailsDTO.from_orm(group)

    @staticmethod
    @use_database
    def search():
        groups = Group.query.all()
        return [GroupSummaryDTO.from_orm(group) for group in groups]

    @staticmethod
    @use_database
    def create(owner_uid: str, group_create_dto: GroupCreateDTO) -> GroupSummaryDTO:
        group = Group.create(**group_create_dto.dict())
        return GroupSummaryDTO.from_orm(group)

    @staticmethod
    @use_database
    def update(group_uid: str, group_update_dto: GroupUpdateDTO) -> GroupSummaryDTO:
        group = Group.get_by_uid(group_uid)
        group.update(**group_update_dto.dict())
        return GroupSummaryDTO.from_orm(group)

    @staticmethod
    @use_database
    def delete(group_uid: int):
        group = Group.get_by_uid(group_uid)
        group_dto = GroupSummaryDTO.from_orm(group)
        group.delete()

    @staticmethod
    @use_database
    def add_member(group_uid, account_uid):
        group = Group.get_by_uid(group_uid)
        account = Account.get_by_uid(account_uid)
        # add given account as group member
        members: List[Account] = group.members
        members.append(account)
        # update group in database
        group.update(members=members)

    @staticmethod
    @use_database
    def remove_member(group_uid, account_uid):
        group = Group.get_by_uid(group_uid)
        account = Account.get_by_uid(account_uid)
        # remove given account from group members
        members: List[Account] = group.members
        members.remove(account)
        # update group in database
        group.update(members=members)
