from pydantic import BaseModel,EmailStr
from .dudi_model import DudiBase
from .alamat_model import AlamatBase

class PembimbingDudiBase(BaseModel) :
    id : int
    username : str
    nama : str
    no_telepon : str
    email : EmailStr
    foto_profile : str | None = None
    jenis_kelamin : str
    token_FCM : str | None = None
    id_dudi : int
    id_sekolah : int
    id_tahun : int

class PembimbingDudiWithAlamatDudi(PembimbingDudiBase) :
    alamat : AlamatBase
    dudi : DudiBase