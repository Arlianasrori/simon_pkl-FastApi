from pydantic import BaseModel,field_validator

from ....models.types import JenisKelaminEnum

class UpdateProfileBody(BaseModel) :
    nis : str | None = None
    nama : str | None = None
    jenis_kelamin : str | None = None
    no_telepon : str | None = None
    id_kelas : int | None = None
    id_jurusan : int | None = None