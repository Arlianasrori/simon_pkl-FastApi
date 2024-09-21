from pydantic import BaseModel
from ...models_domain.dudi_model import DudiWithAlamat
from ...models_domain.common_model import PaginationBase

class KuotaJurusanResponse(BaseModel):
    jurusan : str
    kuota_pria : int
    jumlah_siswa_pria : int
    kuota_wanita : int
    jumlah_siswa_wanita : int

class GetDudiResponse(DudiWithAlamat):
    jumlah_kuota_pria : int
    jumlah_siswa_pria : int
    jumlah_kuota_wanita : int
    jumlah_siswa_wanita : int
    tersedia : bool
    kuota_jurusan : list[KuotaJurusanResponse] = []
    
class FilterGetDudiQuery(BaseModel):
    nama_instansi_perusahaan : str | None = None
    bidang_usaha : str | None = None

class ResponseGetDudiPag(PaginationBase) :
    data : list[GetDudiResponse]