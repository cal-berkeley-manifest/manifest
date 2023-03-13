from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from api.config import Settings


set = Settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationUtilities:

    access_token_expiration_min = set.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expiration_min = set.REFRESH_TOKEN_EXPIRE_MINUTES
    signing_algo = set.JWT_SIGNING_ALGORITHM
    jwt_secret_key = set.JWT_SECRET_KEY
    jwt_refresh_secret_key = set.JWT_REFRESH_SECRET_KEY

    def get_hashed_password(self, password: str) -> str:
        return password_context.hash(password)


    def verify_password(self, password: str, hashed_pass: str) -> bool:
        return password_context.verify(password, hashed_pass)


    def create_access_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        print(f"delta : {expires_delta}")
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=self.access_token_expiration_min)
        
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret_key, self.signing_algo)
        return encoded_jwt

    def create_refresh_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=self.refresh_token_expiration_min)
        
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.jwt_refresh_secret_key, self.signing_algo)
        return encoded_jwt