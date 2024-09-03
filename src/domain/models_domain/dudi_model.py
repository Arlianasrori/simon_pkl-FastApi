from pydantic import BaseModel
from .alamat_model import AlamatBase

class DudiBase(BaseModel):
    id : int
    nama_instansi_perusahaan: str   
    bidang_usaha: str
    no_telepon: str
    deskripsi: str
    tersedia: bool
    id_sekolah : int
    id_tahun : int

class DudiWithAlamat(DudiBase):
    alamat : AlamatBase

class KoutaBase(BaseModel) :
    jumlah_pria: int
    jumlah_wanita: int
class DudiWithAlamatKouta(DudiWithAlamat) :
    kouta : KoutaBase | None = None