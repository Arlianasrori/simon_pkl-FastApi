from pydantic import BaseModel, field_validator
from ....models.types import JenisKelaminEnum

class UpdateAlamat(BaseModel) :
    detail_tempat : str | None = None
    desa : str | None = None
    kecamatan : str | None = None
    kabupaten : str | None = None
    provinsi : str | None = None
    negara : str | None = None

class UpdateProfileBody(BaseModel) :
    nama : str | None = None
    username : str | None = None
    no_telepon : str | None = None
    jenis_kelamin : JenisKelaminEnum | None = None
    token_FCM : str | None = None
    alamat : UpdateAlamat | None = None