from datetime import datetime
from pydantic import BaseModel
from ...models_domain.laporan_kendala_dudi_model import LaporanKendalaDudiWithSiswa

class Filter(BaseModel) :
    id_dudi : int | None = None
    id_siswa : int | None = None

class LaporanKendalaDudiResponse(BaseModel):
    msg: str
    data: dict[str, list[LaporanKendalaDudiWithSiswa]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }