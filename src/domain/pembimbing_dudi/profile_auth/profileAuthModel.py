from pydantic import BaseModel, field_validator
from ....models.types import JenisKelaminEnum


class UpdateProfileBody(BaseModel) :
    nama : str | None = None
    username : str | None = None
    no_telepon : str | None = None
    jenis_kelamin : JenisKelaminEnum | None = None
    token_FCM : str | None = None