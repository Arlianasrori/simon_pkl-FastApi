from datetime import datetime
from pydantic import BaseModel
from ...models_domain.laporan_kendala_model import LaporanKendalaWithSiswa

class Filter(BaseModel) :
    id_dudi : int | None = None
    id_siswa : int | None = None

class LaporanKendalaResponse(BaseModel):
    msg: str
    data: dict[str, list[LaporanKendalaWithSiswa]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }