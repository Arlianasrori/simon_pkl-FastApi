from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.kunjungan_guru_pembimbing_model import KunjunganGuruPembimbingWithDudi

class AddKunjunganBody(BaseModel) :
    id_dudi : int
    tanggal_kunjungan : str
    catatan : str

class UpdateKunjunganBody(BaseModel) :
    id_dudi : int | None = None
    tanggal_kunjungan : str | None = None
    catatan : str | None = None

class ResponseKunjunganDudiPag(PaginationBase) :
    data : list[KunjunganGuruPembimbingWithDudi] = []