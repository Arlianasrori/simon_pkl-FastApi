from pydantic import BaseModel
from datetime import datetime as Datetime
from .siswa_model import SiswaBase,SiswaWithJurusanKelas
from .dudi_model import DudiBase,DudiWithAlamat
from ...models.pengajuanPklModel import StatusPengajuanENUM
class PengajuanPklBase(BaseModel) :
    id : int
    status : StatusPengajuanENUM
    waktu_pengajuan : Datetime
    alasan_pembatalan : str | None = None

class PengajuanPklWithSiswa(PengajuanPklBase) :
    siswa : SiswaBase
    
class PengajuanPklWithSiswaJurusanKelas(PengajuanPklBase) :
    siswa : SiswaWithJurusanKelas

class PengajuanPklWithDudi(PengajuanPklBase) :
    dudi : DudiBase

class PengajuanPklWithDudiAlamat(PengajuanPklBase) :
    dudi : DudiWithAlamat