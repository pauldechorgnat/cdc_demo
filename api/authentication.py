import time
from typing import Dict
from typing import List

import jwt
from fastapi import HTTPException
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from pymongo.collection import Collection

JWT_SECRET = "my_secret"  # TODO: change
JWT_ALGORITHM = "HS256"

# TODO: complexify the three following functions


def check_valid_password(password):
    return len(password) > 0


def encrypt_password(raw_password):
    return raw_password


def decrypt_password(encrypted_password):
    return encrypted_password


def token_response(token: str):
    return {"access_token": token}


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {"user_id": user_id, "expires": time.time() + 60 * 60}  # 1 hour
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception:  # meh
        return {}


class User(BaseModel):
    username: str = "paul_dechorgnat"
    password: str = "***"
    roles: List[str] = ["public"]


class UserLogin(BaseModel):
    username: str = "paul_dechorgnat"
    password: str = "password"


def check_user(user: UserLogin, collection: Collection):
    user_data = collection.find_one(
        filter={"username": user.username, "password": encrypt_password(user.password)}
    )
    if not user_data:
        return False
    return True


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
