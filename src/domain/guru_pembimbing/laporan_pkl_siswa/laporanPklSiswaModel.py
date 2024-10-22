from datetime import datetime
from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase

class FilterBySiswa(BaseModel) : 
    id_siswa : int | None = None
    nama_siswa : str | None = None

class LaporanResponse(BaseModel):
    msg: str
    data: dict[str, list[LaporanPklSiswaBase]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }