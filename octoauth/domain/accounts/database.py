from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from octoauth.architecture.database import DBModel, generate_uid

group_membership = Table(
    "group_members",
    DBModel.metadata,
    Column("account_id", String(36), ForeignKey("accounts.uid"), primary_key=True),
    Column("group_id", String(36), ForeignKey("groups.uid"), primary_key=True),
)


class Account(DBModel):
    __tablename__ = "accounts"

    uid = Column(String(36), primary_key=True, default=generate_uid)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    profile_url = Column(String(300), nullable=True)
    password_hash = Column(String(256), nullable=False)
    groups = relationship("Group", secondary=group_membership, overlaps="members")


class SessionCookie(DBModel):
    __tablename__ = "session_cookies"

    uid = Column(String(36), primary_key=True, default=generate_uid)
    account_uid = Column(String(36), ForeignKey("accounts.uid"), nullable=False, primary_key=True)
    issued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(15), nullable=False)
    country = Column(String(20), nullable=True)
    city = Column(String(30), nullable=True)
    browser = Column(String(20), nullable=True)
    platform = Column(String(20), nullable=True)


class Group(DBModel):
    __tablename__ = "groups"

    uid = Column(String(36), primary_key=True, default=generate_uid)
    name = Column(String(20), nullable=False)
    members = relationship("Account", secondary=group_membership, overlaps="groups")


DBModel.metadata.create_all()
