from pydantic import BaseModel
from datetime import datetime as Datetime
from .siswa_model import SiswaBase
from .dudi_model import DudiBase
from ...models.pengajuanPklModel import StatusPengajuanENUM
class PengajuanPklBase(BaseModel) :
    id : int
    status : StatusPengajuanENUM
    waktu_pengajuan : Datetime

class PengajuanPklWithSiswa(PengajuanPklBase) :
    siswa : SiswaBase

class PengajuanPklWithDudi(PengajuanPklBase) :
    dudi : DudiBase