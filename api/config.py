import os

class Settings:
    try:
        CORE_MONGO_CONN                 = os.environ["MONGODB_URL"]
        AUTH_MONGO_CONN                 = os.environ["AUTH_MONGODB_URL"]

        JWT_SECRET_KEY                  = os.environ["JWT_SECRET_KEY"]
        JWT_REFRESH_SECRET_KEY          = os.environ["JWT_REFRESH_SECRET_KEY"]
        ACCESS_TOKEN_EXPIRE_MINUTES     = 30 # In Min
        REFRESH_TOKEN_EXPIRE_MINUTES    = 60 * 24 # 24 hrs in min
        JWT_SIGNING_ALGORITHM           = "HS256"

    except Exception as e:
        raise e 

