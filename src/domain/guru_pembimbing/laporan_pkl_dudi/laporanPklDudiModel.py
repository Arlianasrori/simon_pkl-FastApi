from datetime import datetime
from pydantic import BaseModel
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase

class Filter(BaseModel) :
    id_dudi : int | None = None

class LaporanDudiResponse(BaseModel):
    msg: str
    data: dict[str, list[LaporanPklDudiBase]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }