"""
Models defined in this files are objects used to perform
database queries in an object-oriented style...
"""
from sqlalchemy import Column, DateTime, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from octoauth.architecture.database import DBModel, generate_uid


class Application(DBModel):
    """
    ORM object that represents an oauth2 application in the database.
    """

    __tablename__ = "applications"

    uid = Column(String(36), primary_key=True, default=generate_uid)
    name = Column(String(40), unique=True, nullable=False)
    description = Column(String(500), nullable=False)
    client_id = Column(String(36), unique=True)
    client_secret = Column(String(256), default=generate_uid, nullable=False)
    icon_uri = Column(String(200), nullable=True)


class AuthorizedRedirectURI(DBModel):
    __tablename__ = "authorized_redirect_uris"

    uid = Column(String(36), primary_key=True, default=generate_uid)
    application_uid = Column(String(36), ForeignKey("applications.uid"), nullable=False)
    redirect_uri = Column(String(200), nullable=True)


class Scope(DBModel):
    """
    ORM object that represents an oauth2 scope in the database.
    """

    __tablename__ = "scopes"

    code = Column(String(36), default=generate_uid, primary_key=True)
    description = Column(String(300), nullable=False)


class Grant(DBModel):
    """
    Base columns required to defines a grant (account, client, scope)
    """

    __tablename__ = "grants"
    __table_args__ = (UniqueConstraint("account_uid", "client_id", "scope_code", name="uc_unique_grant"),)

    id = Column(Integer, primary_key=True)
    account_uid = Column(String(36), ForeignKey("accounts.uid"))
    client_id = Column(String(36), ForeignKey("applications.client_id"))
    scope_code = Column(String(36), ForeignKey("scopes.code"))


refresh_token_grants = Table(
    "refresh_token_grants",
    DBModel.metadata,
    Column("refresh_token", ForeignKey("refresh_tokens.refresh_token", ondelete="CASCADE"), primary_key=True),
    Column("grant_id", ForeignKey("grants.id"), primary_key=True),
)


class RefreshToken(DBModel):
    """
    ORM object that represents a refresh token and its grant information.
    """

    __tablename__ = "refresh_tokens"

    refresh_token = Column(String(36), primary_key=True, default=generate_uid)
    expires = Column(DateTime, nullable=False)
    account_uid = Column(String(36), ForeignKey("accounts.uid"), nullable=False)
    client_id = Column(String(36), ForeignKey("applications.client_id"), nullable=False)

    grants = relationship("Grant", secondary=refresh_token_grants)


authorization_code_grants = Table(
    "authorization_code_grants",
    DBModel.metadata,
    Column("authorization_code", ForeignKey("authorization_codes.code", ondelete="CASCADE"), primary_key=True),
    Column("grant_id", ForeignKey("grants.id"), primary_key=True),
)


class AuthorizationCode(DBModel):
    """
    ORM object that represents an authorization code and its grant information.
    """

    __tablename__ = "authorization_codes"

    code = Column(String(36), primary_key=True, default=generate_uid)
    account_uid = Column(String(36), ForeignKey("accounts.uid"), nullable=False)
    client_id = Column(String(36), ForeignKey("applications.client_id"), nullable=False)

    expires = Column(DateTime, nullable=False)

    code_challenge = Column(String(88), nullable=True)
    code_challenge_method = Column(String(8), nullable=True)

    grants = relationship("Grant", secondary=authorization_code_grants)


DBModel.metadata.create_all()
