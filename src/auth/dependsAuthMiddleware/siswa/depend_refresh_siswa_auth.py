from fastapi import Cookie, Request,Header

from ....models.siswaModel import Siswa
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os

SECRET_KEY = os.getenv("SISWA_SECRET_REFRESH_TOKEN")

async def siswaDependAuth(refresh_token : str | None = Cookie(None),Authorization: str = Header(default=None,example="jwt access token"),req : Request = None,Session : sessionDepedency = None) :
    try :
        if refresh_token :
            token = refresh_token
        elif Authorization :
            token = Authorization.split(" ")[1]
        
        if not token :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        siswa = jwt.decode(token,SECRET_KEY,algorithms="HS256")

        if not siswa :
            raise HttpException(status=401,message="invalid token(unauthorized)")
        
        selectQuery = select(Siswa.id,Siswa.nama,Siswa.token_FCM,Siswa.jenis_kelamin,Siswa.id_sekolah).where(Siswa.id == siswa["id"])
        exec = await Session.execute(selectQuery)
        findSiswa = exec.first()

        if not findSiswa : 
            raise HttpException(status=401,message="invalid token(unauthorized)")
        req.siswa = findSiswa._asdict()
    except JWTError as error:
       raise HttpException(status=401,message=str(error.args[0])) 
