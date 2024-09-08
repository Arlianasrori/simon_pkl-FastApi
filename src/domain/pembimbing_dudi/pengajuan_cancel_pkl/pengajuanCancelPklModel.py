from pydantic import BaseModel
from ...models_domain.pengajuan_cancel_pkl_model import PengajuanCancelPklWithSiswa
from ...models_domain.common_model import PaginationBase
from enum import Enum

class AccPengajuanEnum(Enum) :
    SETUJU : str = "setuju"
    TIDAK_SETUJU : str = "tidak setuju"

class AccDccPengajuanPkl(BaseModel) :
    status : AccPengajuanEnum

class ResponsePengajuanCancelPklPag(PaginationBase) :
    data : list[PengajuanCancelPklWithSiswa]