from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
import os
from ..error.errorHandling import HttpException

from ..models.types import UserTypeEnum
from ..models.siswaModel import Siswa
from ..models.guruPembimbingModel import GuruPembimbing
from ..models.pembimbingDudiModel import PembimbingDudi
from ..models.sekolahModel import Admin
userList = [
    {
        "type" : UserTypeEnum.SISWA,
        "modelDb" : Siswa,
        "secret_key" : os.getenv("SISWA_SECRET_ACCESS_TOKEN")
    },
    {
        "type" : UserTypeEnum.GURU,
        "modelDb" : GuruPembimbing,
        "secret_key" : os.getenv("GURU_PEMBIMBING_SECRET_ACCESS_TOKEN")
    },
    {
        "type" : UserTypeEnum.PEMBIMBING_DUDI,
        "modelDb" : PembimbingDudi,
        "secret_key" : os.getenv("PEMBIMBING_DUDI_SECRET_ACCESS_TOKEN")
    },
    {
        "type" : UserTypeEnum.ADMIN,
        "modelDb" : Admin,
        "secret_key" : os.getenv("ADMIN_SECRET_ACCESS_TOKEN")
    }
]

def get_user_by_type(type_user):
    return next((item for item in userList if item["type"] == type_user), None)

async def auth_middleware(token: str | None,type,session : AsyncSession):
    user = get_user_by_type(type)
    if user:
        try:
            # Check if a token is present
            print(token)
            if not token:
                raise HttpException(status=401, message="invalid token(unauthorized)")
            
            # Decode and verify the JWT token
            userDecode = jwt.decode(token, user["secret_key"], algorithms="HS256")

            # Check if student information exists in the decoded token
            if not userDecode:
                raise HttpException(status=401, message="invalid token(unauthorized)")
            
            # Create a select query to find the student in the database
            selectQuery = select(user["modelDb"].id).where(user["modelDb"].id == userDecode["id"])
            exec = await session.execute(selectQuery)
            findUser = exec.first()

            # Check if the student exists in the database
            if not findUser:
                raise HttpException(status=401, message="invalid token(unauthorized)")
            
            return {
                "user_id" : userDecode["id"],
                "type_user" : user["type"]
            }
        except JWTError as error:
            # Handle JWT decoding errors
            raise HttpException(status=401, message=str(error.args[0]))