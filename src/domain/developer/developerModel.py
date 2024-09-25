from pydantic import BaseModel, field_validator,EmailStr

class Developer(BaseModel) :
    id : int
    username : str
    no_telepon : str
    email : EmailStr

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
    no_telepon : str
    email : EmailStr

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class UpdateAdminBody(BaseModel) :
    username : str | None = None
    password : str | None = None
    no_telepon : str | None = None
    email : EmailStr | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v