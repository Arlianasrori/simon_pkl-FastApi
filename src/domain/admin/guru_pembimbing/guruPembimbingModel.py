from pydantic import BaseModel,field_validator,EmailStr
from ....models.types import JenisKelaminEnum
from ...models_domain.common_model import PaginationBase
from ...models_domain.guru_pembimbing_model import GuruPembimbingWithAlamat


class AddGuruPembimbingBody(BaseModel):
    nip : str
    nama : str
    no_telepon : str
    email : EmailStr
    jenis_kelamin : JenisKelaminEnum
    tempat_lahir : str
    tanggal_lahir : str         
    agama : str 
    id_tahun : int
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class UpdateGuruPembimbingBody(BaseModel):
    nip : str | None = None
    nama : str | None = None
    no_telepon : str | None = None
    email : EmailStr | None = None
    jenis_kelamin : JenisKelaminEnum | None = None
    tempat_lahir : str | None = None
    tanggal_lahir : str | None = None         
    agama : str | None = None
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class ResponseGuruPembimbingPag(PaginationBase) :
    data : list[GuruPembimbingWithAlamat] = []