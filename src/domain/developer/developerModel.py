from pydantic import BaseModel, field_validator

class Developer(BaseModel) :
    id : int
    username : str

class AddSekolahBody(BaseModel) :
    npsn : str
    nama : str

class UpdateSekolahBody(BaseModel) :
    npsn : str | None = None
    nama : str | None = None

# admin
class AddAdminBody(BaseModel) :
    id_sekolah : int
    username : str
    password : str

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class UpdateAdminBody(BaseModel) :
    username : str | None = None
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v