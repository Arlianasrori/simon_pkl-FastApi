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

class KuotaJurusanBase(BaseModel) :
    id : int
    jumlah_pria : int
    jumlah_wanita : int
    jurusan : JurusanBase

class KuotaBase(BaseModel) :
    id : int
    jumlah_pria: int
    jumlah_wanita: int
    kuota_jurusan : list[KuotaJurusanBase] | None = None

class DudiWithAlamatKuota(DudiWithAlamat) :
    kuota : KuotaBase | None = None

class DudiWithKuota(DudiBase) :
    kuota : KuotaBase | None = None