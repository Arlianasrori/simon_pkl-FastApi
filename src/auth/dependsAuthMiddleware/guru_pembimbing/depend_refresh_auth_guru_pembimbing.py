from fastapi import Cookie, Request,Header

from ....models.guruPembimbingModel import GuruPembimbing
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

SECRET_KEY = os.getenv("GURU_PEMBIMBING__REFRESH_ACCESS_TOKEN")

async def guruPembimbingRefreshAuth(refresh_token : str | None = Cookie(None),Authorization: str = Header(default=None,example="jwt access token"),req : Request = None,Session : sessionDepedency = None) :
    try :
        if refresh_token :
            token = refresh_token
        elif Authorization :
            token = Authorization.split(" ")[1]
        
        if not token :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        guruPembimbing = jwt.decode(token,SECRET_KEY,algorithms="HS256")

        if not guruPembimbing :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        selectQuery = select(GuruPembimbing.id,GuruPembimbing.nama,GuruPembimbing.token_FCM,GuruPembimbing.id_sekolah).where(GuruPembimbing.id == guruPembimbing["id"])
        exec = await Session.execute(selectQuery)
        findGuruPembimbing = exec.first()

        if not findGuruPembimbing : 
            raise HttpException(status=401,message="invalid token(unauthorized)")
        req.guruPembimbing = findGuruPembimbing._asdict()
    except JWTError as error:
       raise HttpException(status=401,message=str(error.args[0])) 
