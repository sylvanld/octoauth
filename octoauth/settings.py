import os
from dataclasses import dataclass
from datetime import timedelta
from typing import List


def getenv(variable_name: str, default=None):
    value = os.getenv(variable_name)
    if value is None and default is None:
        raise ValueError(f"Missing environment variable {variable_name}")
    return value or default

def get_boolean_env(variable_name: str, default=None):
    value = getenv(variable_name, default)
    if value == "true":
        return True
    elif value == "false":
        return False
    raise ValueError(f"Invalid boolean value for variable {variable_name}. Expected one of: true, false.")

def file_content(filename) -> str:
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


@dataclass
class Settings:
    API_TITLE: str
    API_DESCRIPTION: str
    API_VERSION: str
    API_TAGS_METADATA: List[dict]

    ACCESS_TOKEN_EXPIRES: timedelta
    ACCESS_TOKEN_PRIVATE_KEY: str
    ACCESS_TOKEN_PUBLIC_KEY: str

    ACCOUNT_DASHBOARD_URL: str
    DATABASE_URI: str

    MAILING_ENABLED: bool
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    AUTHORIZATION_CODE_EXPIRES: timedelta
    REFRESH_TOKEN_EXPIRES: timedelta
    SESSION_COOKIE_LIFETIME: timedelta


SETTINGS = Settings(
    API_TITLE="OctoAuth API",
    API_DESCRIPTION=("Custom SSO inspired from OIDC that exposes account management Rest services."),
    API_VERSION="0.0.1",
    API_TAGS_METADATA=[
        {"name": "accounts", "description": "Manage user account."},
        {"name": "groups", "description": "Manage groups and memberships."},
    ],
    DATABASE_URI=getenv("OCTOAUTH_DATABASE_URL"),
    ACCOUNT_DASHBOARD_URL=getenv("ACCOUNT_DASHBOARD_URL"),
    ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
    ACCESS_TOKEN_PRIVATE_KEY=file_content(getenv("OCTOAUTH_JWT_PRIVATE_KEY_PATH", "assets/private-key.pem")),
    ACCESS_TOKEN_PUBLIC_KEY=file_content("assets/public-key.pem"),
    MAILING_ENABLED=get_boolean_env("OCTOAUTH_MAILING_ENABLED"),
    SMTP_HOST="smtp.gmail.com",
    SMTP_PORT=587,
    SMTP_USERNAME="python27bot@gmail.com",
    SMTP_PASSWORD="bcvpeehtvxoixmao",
    AUTHORIZATION_CODE_EXPIRES=timedelta(seconds=15),
    REFRESH_TOKEN_EXPIRES=timedelta(days=10),
    SESSION_COOKIE_LIFETIME=timedelta(days=30),
)
