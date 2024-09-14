from pydantic import BaseModel
from datetime import datetime 
from ....models_domain.absen_model import AbsenWithSiswaDudi 

class FilterAbsen(BaseModel) :
    year : int | None = None
    month : int | None = None
    day : int | None = None
    id_siswa : int | None = None
    nama : str | None = None

class AbsenResponse(BaseModel):
    msg: str
    data: dict[datetime, list[AbsenWithSiswaDudi]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }