from pydantic import BaseModel
from .siswa_model import SiswaBase
from .dudi_model import DudiBase,DudiWithAlamat
from ...models.pengajuanPklModel import StatusCancelPKLENUM
from datetime import datetime

class PengajuanCancelPklBase(BaseModel) :
    id : int
    status : StatusCancelPKLENUM
    waktu_pengajuan : datetime
    alasan : str

class PengajuanCancelPklWithSiswa(PengajuanCancelPklBase) :
    siswa : SiswaBase

class PengajuanCancelPklWithDudi(PengajuanCancelPklBase) :
    dudi : DudiBase

class PengajuanCancelPklWithDudiAlamat(PengajuanCancelPklBase) :
    dudi : DudiWithAlamat