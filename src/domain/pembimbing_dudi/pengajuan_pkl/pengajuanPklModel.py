from pydantic import BaseModel
from ...models_domain.pengajuan_pkl_model import PengajuanPklWithSiswa
from ...models_domain.common_model import PaginationBase
from enum import Enum

class AccPengajuanEnum(Enum) :
    SETUJU : str = "setuju"
    TIDAK_SETUJU : str = "tidak_setuju"

class AccDccPengajuanPkl(BaseModel) :
    status : AccPengajuanEnum

class ResponsePengajuanPklPag(PaginationBase) :
    data : list[PengajuanPklWithSiswa]