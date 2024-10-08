from pydantic import BaseModel,field_validator

from ....models.types import JenisKelaminEnum

class UpdateProfileBody(BaseModel) :
    nip : str | None = None
    nama : str | None = None
    no_telepon : str | None = None
    jenis_kelamin : JenisKelaminEnum | None = None
    tempat_lahir : str | None = None
    tanggal_lahir : str | None = None         
    agama : str | None = None
    token_FCM : str | None = None