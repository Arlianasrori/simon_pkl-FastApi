from pydantic import BaseModel,field_validator

from ....models.types import JenisKelaminEnum

class UpdateProfileBody(BaseModel) :
    nis : str | None = None
    nama : str | None = None
    jenis_kelamin : str | None = None
    no_telepon : str | None = None
    id_kelas : int | None = None
    id_jurusan : int | None = None
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v