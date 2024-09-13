from pydantic import BaseModel,field_validator
from ...models_domain.common_model import PaginationBase
from ...models_domain.pembimbing_dudi_model import PembimbingDudiWithAlamatDudi

class AddPembimbingDudiBody(BaseModel) :
    nama : str
    username : str
    no_telepon : str
    jenis_kelamin : str
    id_dudi : int
    id_tahun : int
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class UpdatePembimbingDudiBody(BaseModel) :
    nama : str | None = None
    username : str | None = None
    no_telepon : str | None = None
    jenis_kelamin : str | None = None
    id_dudi : int | None = None
    password : str | None = None

    @field_validator("password")
    def validate_password(cls, v):
        if " " in v:
            raise ValueError("password tidak bisa mengandung spasi")
        return v

class ResponsePembimbingDudiPagination(PaginationBase) :
    data : list[PembimbingDudiWithAlamatDudi] = []
