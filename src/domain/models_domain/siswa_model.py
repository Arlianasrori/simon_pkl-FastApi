from pydantic import BaseModel
from .alamat_model import AlamatBase
from .kelas_jurusan_model import JurusanBase,KelasBase
from .guru_pembimbing_model import GuruPembimbingBase
from ...models.siswaModel import StatusPKLEnum

class SiswaBase(BaseModel) :
    id : int
    nis : str
    nama : str
    jenis_kelamin : str
    no_telepon : str
    status : StatusPKLEnum
    token_FCM : str | None = None
    foto_profile : str | None = None

class SiswaWithAlamat(SiswaBase) :
    alamat : AlamatBase

class MoreSiswa(SiswaBase) :
    jurusan : JurusanBase
    kelas : KelasBase
    guru_pembimbing : GuruPembimbingBase | None = None

class DetailSiswa(MoreSiswa) :
    pass
    # dudi : DudiBase
    # pembimbing_dudi : PembimbingDudiBase
    