from pydantic import BaseModel
from .siswa_model import SiswaBase
from .dudi_model import DudiBase
from ...models.pengajuanPklModel import StatusCancelPKLENUM

class PengajuanCancelPklBase(BaseModel) :
    id : int
    status : StatusCancelPKLENUM

class PengajuanCancelPklWithSiswa(PengajuanCancelPklBase) :
    siswa : SiswaBase

class PengajuanCancelPklWithDudi(PengajuanCancelPklBase) :
    dudi : DudiBase