from pydantic import BaseModel,EmailStr
from ...models_domain.common_model import PaginationBase
from ...models_domain.dudi_model import DudiWithAlamat

class AddDudiBody(BaseModel):
    nama_instansi_perusahaan: str
    bidang_usaha: str
    no_telepon: str
    email : EmailStr
    deskripsi: str
    id_tahun : int

class UpdateDudiBody(BaseModel):
    nama_instansi_perusahaan: str | None = None
    bidang_usaha: str | None = None
    no_telepon: str | None = None
    deskripsi: str | None = None

class ResponseDudiPag(PaginationBase):
    data : list[DudiWithAlamat] = []

