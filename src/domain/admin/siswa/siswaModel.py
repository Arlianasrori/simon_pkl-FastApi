from pydantic import BaseModel,field_validator,EmailStr
from ....models.siswaModel import StatusPKLEnum
from ...models_domain.common_model import PaginationBase
from ...models_domain.siswa_model import MoreSiswa

class AddSiswaBody(BaseModel) :
    nis : str
    nama : str
    jenis_kelamin : str
    no_telepon : str
    email : EmailStr
    id_kelas : int
    id_jurusan : int
    id_guru_pembimbing : int | None = None
    id_tahun : int
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class UpdateSiswaBody(BaseModel) :
    nis : str | None = None
    nama : str | None = None
    jenis_kelamin : str | None = None
    no_telepon : str | None = None
    email : EmailStr | None = None
    status : StatusPKLEnum | None = None
    id_kelas : int | None = None
    id_jurusan : int | None = None
    id_guru_pembimbing : int | None = None
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class ResponseSiswaPag(PaginationBase) :
    data : list[MoreSiswa] = []