import time
from enum import auto
from typing import Dict
from typing import List

import jwt
from fastapi import HTTPException
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from fastapi_utils.enums import StrEnum
from pydantic import BaseModel
from pymongo.collection import Collection

from .config import JWT_ALGORITHM
from .config import JWT_SECRET

# TODO: complexify the three following functions


def check_valid_password(password):
    return len(password) > 6


def encrypt_password(raw_password):
    return raw_password


def decrypt_password(encrypted_password):
    return encrypted_password


def token_response(token: str):
    return {"access_token": token}


def signJWT(
    user_id: str, secret: str = JWT_SECRET, algorithm: str = JWT_ALGORITHM
) -> Dict[str, str]:
    payload = {"user_id": user_id, "expires": time.time() + 60 * 60}  # 1 hour
    token = jwt.encode(payload, secret, algorithm=algorithm)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception:  # meh
        return {}


class RoleName(StrEnum):
    public = auto()
    contributor = auto()
    corrector = auto()
    admin = auto()


class User(BaseModel):
    username: str = "paul_dechorgnat"
    password: str = "***"
    roles: List[RoleName] = ["public"]


class UserLogin(BaseModel):
    username: str = "paul_dechorgnat"
    password: str = "password"


def check_user(user: UserLogin, collection: Collection):
    user_data = collection.find_one(
        filter={"username": user.username, "password": encrypt_password(user.password)}
    )
    return user_data is not None


class UserData(BaseModel):
    password: str = None
    roles: List[RoleName] = None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except Exception:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


def check_permissions(
    username: str,
    route_name: str,
    user_collection: Collection,
    role_collection: Collection,
) -> bool:

    user_data = user_collection.find_one(filter={"username": username})

    roles = user_data["roles"]

    command = [
        {"$match": {"role": {"$in": roles}}},
        {"$project": {"permissions": "$permissions"}},
        {"$unwind": "$permissions"},
        {
            "$group": {
                "_id": "permissions",
                "permissions": {"$addToSet": "$permissions"},
            }
        },
    ]

    results = list(role_collection.aggregate(command))[0]["permissions"]

    if route_name in results:
        return roles
    else:
        return False
