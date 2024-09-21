from pydantic import BaseModel
from ...models_domain.dudi_model import DudiWithAlamat
from ...models_domain.common_model import PaginationBase

class GetDudiResponse(DudiWithAlamat):
    jumlah_kouta_pria : int
    jumlah_siswa_pria : int
    jumlah_kouta_wanita : int
    jumlah_siswa_wanita : int
    tersedia : bool
    
class FilterGetDudiQuery(BaseModel):
    nama_instansi_perusahaan : str | None = None
    bidang_usaha : str | None = None

class ResponseGetDudiPag(PaginationBase) :
    data : list[GetDudiResponse]