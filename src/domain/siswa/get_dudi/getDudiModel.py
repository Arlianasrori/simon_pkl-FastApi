from pydantic import BaseModel
from ...models_domain.dudi_model import DudiWithAlamat
from ...models_domain.common_model import PaginationBase

class KoutaJurusanResponse(BaseModel):
    jurusan : str
    kouta_pria : int
    jumlah_siswa_pria : int
    kouta_wanita : int
    jumlah_siswa_wanita : int

class GetDudiResponse(DudiWithAlamat):
    jumlah_kouta_pria : int
    jumlah_siswa_pria : int
    jumlah_kouta_wanita : int
    jumlah_siswa_wanita : int
    tersedia : bool
    kouta_jurusan : list[KoutaJurusanResponse] = []
    
class FilterGetDudiQuery(BaseModel):
    nama_instansi_perusahaan : str | None = None
    bidang_usaha : str | None = None

class ResponseGetDudiPag(PaginationBase) :
    data : list[GetDudiResponse]