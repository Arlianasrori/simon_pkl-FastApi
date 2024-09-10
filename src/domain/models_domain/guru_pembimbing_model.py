from pydantic import BaseModel
from ...models.types import JenisKelaminEnum
from .alamat_model import AlamatBase
from .sekolah_model import SekolahBase

class GuruPembimbingBase(BaseModel):
    id : int
    nip : str
    nama : str
    no_telepon : str
    jenis_kelamin : JenisKelaminEnum
    tempat_lahir : str
    tanggal_lahir : str         
    agama : str 
    foto_profile : str | None
    token_FCM : str | None
    id_sekolah : int
    id_tahun : int

class GuruPembimbingWithAlamat(GuruPembimbingBase):
    alamat : AlamatBase

class GuruPembimbingWithSekolahAlamat(GuruPembimbingWithAlamat):
    sekolah : SekolahBase