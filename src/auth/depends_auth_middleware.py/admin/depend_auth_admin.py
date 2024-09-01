from fastapi import Cookie, Request

from ....models.sekolahModel import Admin
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

SECRET_KEY = os.getenv("ADMIN_SECRET_ACCESS_TOKEN")

async def adminCookieAuth(access_token : str | None = Cookie(None),req : Request = None,Session : sessionDepedency = None) :
    print(access_token)
    if not access_token :
        raise HttpException(status=401,message="invalid token(unauthorized)")
    try :
        admin = jwt.decode(access_token,SECRET_KEY,algorithms="HS256")

        if not admin :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        selectQuery = select(Admin.id,Admin.username,Admin.id_sekolah).where(Admin.id == admin["id"])
        exec = await Session.execute(selectQuery)
        findAdmin = exec.first()

        if not findAdmin : 
            raise HttpException(status=401,message="invalid token(unauthorized)")
        req.admin = findAdmin._asdict()
    except JWTError as error:
       raise HttpException(status=401,message=str(error.args[0])) 