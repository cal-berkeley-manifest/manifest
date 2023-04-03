from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from api.config import Settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from api.schemas import *
import json


set = Settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/authenticate",
    scheme_name="JWT"
)

access_token_expiration_min = set.ACCESS_TOKEN_EXPIRE_MINUTES
refresh_token_expiration_min = set.REFRESH_TOKEN_EXPIRE_MINUTES
signing_algo = set.JWT_SIGNING_ALGORITHM
jwt_secret_key = set.JWT_SECRET_KEY
jwt_refresh_secret_key = set.JWT_REFRESH_SECRET_KEY

class AuthenticationUtilities:



    def get_hashed_password(self, password: str) -> str:
        return password_context.hash(password)


    def verify_password(self, password: str, hashed_pass: str) -> bool:
        return password_context.verify(password, hashed_pass)


    def create_access_token(self, subject: Union[str, Any], role: list , expires_delta: int = None) -> str:
        print(f"delta : {expires_delta}")
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=access_token_expiration_min)
        
        to_encode = {"exp": expires_delta, "sub": str(subject), "role": role }
        encoded_jwt = jwt.encode(to_encode, jwt_secret_key, signing_algo)
        return encoded_jwt

    def create_refresh_token(self, subject: Union[str, Any], role: list, expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=refresh_token_expiration_min)
        
        to_encode = {"exp": expires_delta, "sub": str(subject), "role": role }
        encoded_jwt = jwt.encode(to_encode, jwt_refresh_secret_key, signing_algo)
        return encoded_jwt


class Authenticator:

    def __init__(self, roles: list):
        self.roles = roles
        print("authenticator")
    
    def __call__(self, token: str = Depends(reuseable_oauth)):
        print(self.roles)
        try:
            payload = jwt.decode(
                token, jwt_secret_key, algorithms=[signing_algo]
            )
            token_data = TokenPayload(**payload)

            if datetime.fromtimestamp(token_data.exp) < datetime.now() or not any(role in list(token_data.role) for role in self.roles):
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired or not permitted",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except(jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return True


