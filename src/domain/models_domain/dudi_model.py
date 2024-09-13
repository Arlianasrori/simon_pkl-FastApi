from pydantic import BaseModel
from .alamat_model import AlamatBase
from .siswa_model import JurusanBase

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

class KoutaJurusanBase(BaseModel) :
    id : int
    jumlah_pria : int
    jumlah_wanita : int
    jurusan : JurusanBase

class KoutaBase(BaseModel) :
    id : int
    jumlah_pria: int
    jumlah_wanita: int
    kouta_jurusan : list[KoutaJurusanBase] | None = None

class DudiWithAlamatKouta(DudiWithAlamat) :
    kouta : KoutaBase | None = None

class DudiWithKouta(DudiBase) :
    kouta : KoutaBase | None = None