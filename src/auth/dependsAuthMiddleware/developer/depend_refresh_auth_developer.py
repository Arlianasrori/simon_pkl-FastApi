from fastapi import Cookie, Request

from ....models.developerModel import Developer
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

SECRET_KEY = os.getenv("DEVELOPER_SECRET_REFRESH_TOKEN")

async def developerRefreshAuth(refresh_token : str | None = Cookie(None),req : Request = None,Session : sessionDepedency = None) :
    print(refresh_token)
    if not refresh_token :
        raise HttpException(status=401,message="invalid token(unauthorized)")
    try :
        developer = jwt.decode(refresh_token,SECRET_KEY,algorithms="HS256")

        if not developer :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        selectQuery = select(Developer.id,Developer.username).where(Developer.id == developer["id"])
        exec = await Session.execute(selectQuery)
        findeDeveloper = exec.first()

        if not findeDeveloper : 
            raise HttpException(status=401,message="invalid token(unauthorized)")
        req.developer = findeDeveloper._asdict()
    except JWTError as error:
       raise HttpException(status=401,message=str(error.args[0])) 
