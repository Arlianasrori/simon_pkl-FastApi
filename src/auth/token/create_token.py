import os
from jose import JWTError, jwt

from ...error.errorHandling import HttpException
import enum

class CreateTokenEnum(enum.Enum) :
    SISWA = "SISWA"
    GURU_PEMBIMBING = "GURU_PEMBIMBING"
    DEVELOPER = "DEVELOPER"
    ADMIN = "ADMIN"
    PEMBIMBING_DUDI = "PEMBIMBING_DUDI"

def create_token(data : dict,type : CreateTokenEnum) :
    try :
        access_env = f"{type.value}_SECRET_ACCESS_TOKEN"
        refresh_env = f"{type.value}_SECRET_REFRESH_TOKEN"
        ACCESS_KEY = os.getenv(access_env)
        REFRESH_KEY = os.getenv(refresh_env)

        if not ACCESS_KEY or not REFRESH_KEY :
            raise HttpException(status=500,message="SECRET KEY NOT FOUND")
        
        access_token = jwt.encode(data,ACCESS_KEY,algorithm="HS256")
        refresh_token = jwt.encode(data,REFRESH_KEY,algorithm="HS256")
        return {"access_token" : access_token,"refresh_token" : refresh_token}
    except JWTError as Error:
        raise HttpException(status=400,message=Error.args)