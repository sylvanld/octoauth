import os
import uuid
import requests

from datetime import datetime, timedelta

import jwt
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from octoauth.settings import SETTINGS

SCRYPT_PARAMS = {"length": 32, "n": 2 ** 14, "r": 8, "p": 1}


def hash_password(password: str) -> str:
    """
    Generate password hash (salt + key) on 64 bytes.
    """
    salt = os.urandom(16)
    kdf = Scrypt(salt=salt, **SCRYPT_PARAMS)
    key = kdf.derive(password.encode("utf-8")).hex()
    return salt.hex() + "$" + key


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Compare password with given hash and return True
    if they are the same, False otherwise.
    """
    salt, key = [bytes.fromhex(item) for item in hashed_password.split("$")]
    kdf = Scrypt(salt=salt, **SCRYPT_PARAMS)
    try:
        kdf.verify(password.encode("utf-8"), key)
    except InvalidKey:
        return False
    return True


def generate_access_token(*, client_id: str, expires: timedelta, scope: str = None, account_uid: str = None):
    """
    Generate an access token that can be a personal access token or an application token.
    """
    now = datetime.now()
    expiration_date = now + expires

    return jwt.encode(
        {
            "exp": expiration_date.timestamp(),
            "sub": account_uid,
            "iat": now.timestamp(),
            "scope": scope,
        },
        SETTINGS.ACCESS_TOKEN_PRIVATE_KEY,
        algorithm="RS256",
    )


def decode_access_token(token: str):
    """
    Retrieve information contained in an access token.
    """
    return jwt.decode(token, SETTINGS.ACCESS_TOKEN_PUBLIC_KEY, algorithms=["RS256"])


def generate_refresh_token():
    """
    Generate a refresh token that contains no other information.
    """
    return uuid.uuid4().hex + uuid.uuid4().hex


def get_ip_info(ip_address) -> dict:
    """
    Get IP address info
    """
    info = dict(ip=ip_address)
    
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        response_data = response.json()
        info.update(
            city=response_data["city"], 
            country=response_data["country_name"]
        )
    except Exception:
        # handle all exceptions as error here should never be blocking.
        pass
    
    return info