from fastapi import Cookie, Request,Header

from ....models.pembimbingDudiModel import PembimbingDudi
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

SECRET_KEY = os.getenv("PEMBIMBING_DUDI_SECRET_REFRESH_TOKEN")

async def pembimbingDudiRefreshAuth(refresh_token : str | None = Cookie(None),Authorization: str = Header(default=None,example="jwt access token"),req : Request = None,Session : sessionDepedency = None) :
    try :
        token = None
        if refresh_token :
            token = refresh_token
        elif Authorization :
            token = Authorization.split(" ")[1]

        if not token :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        pemimbingDudi = jwt.decode(token,SECRET_KEY,algorithms="HS256")

        if not pemimbingDudi :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        selectQuery = select(PembimbingDudi.id,PembimbingDudi.nama,PembimbingDudi.token_FCM,PembimbingDudi.id_sekolah).where(PembimbingDudi.id == pemimbingDudi["id"])
        exec = await Session.execute(selectQuery)
        findPembimbingDudi = exec.first()

        if not findPembimbingDudi : 
            raise HttpException(status=401,message="invalid token(unauthorized)")
        req.pembimbingDudi = findPembimbingDudi._asdict()
    except JWTError as error:
       raise HttpException(status=401,message=str(error.args[0])) 
