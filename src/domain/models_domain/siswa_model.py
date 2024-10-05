from pydantic import BaseModel,EmailStr
from .alamat_model import AlamatBase
from .kelas_jurusan_model import JurusanBase,KelasBase
from .guru_pembimbing_model import GuruPembimbingBase
from ...models.siswaModel import StatusPKLEnum
from .dudi_model import DudiBase
from .pembimbing_dudi_model import PembimbingDudiBase

class SiswaBase(BaseModel) :
    id : int
    nis : str
    nama : str
    jenis_kelamin : str
    email : EmailStr
    no_telepon : str
    status : StatusPKLEnum
    token_FCM : str | None = None
    foto_profile : str | None = None

class SiswaWithAlamat(SiswaBase) :
    alamat : AlamatBase | None = None

class SiswaWithJurusanKelas(SiswaWithAlamat) :
    jurusan : JurusanBase
    kelas : KelasBase

class MoreSiswa(SiswaWithJurusanKelas) :
    guru_pembimbing : GuruPembimbingBase | None = None

class DetailSiswa(MoreSiswa) :
    dudi : DudiBase | None = None
    pembimbing_dudi : PembimbingDudiBase | None = None

class SiswaWithDudi(SiswaWithJurusanKelas) :
    dudi : DudiBase
    
class SiswaWithDudiWithOutKelasJurusan(SiswaBase) :
    dudi : DudiBase