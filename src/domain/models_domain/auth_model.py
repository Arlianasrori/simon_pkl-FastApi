from pydantic import BaseModel
from enum import Enum

class RoleEnum(Enum) :
    ADMIN = "admin"
    DEVELOPER = "developer"
    GURU_PEMBIMBING = "guru pembimbing"
    PEMBIMBING_DUDI = "pembimbing dudi"
    SISWA = "siswa"

class ResponseAuthToken(BaseModel) :
    role : RoleEnum
    access_token : str
    refresh_token : str

class ResponseRefreshToken(BaseModel) :
    access_token : str
    refresh_token : str
