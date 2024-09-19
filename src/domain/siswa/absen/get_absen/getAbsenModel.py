from pydantic import BaseModel
from datetime import datetime 
from ....models_domain.absen_model import MoreAbsen 

class FilterAbsen(BaseModel) :
    year : int | None = None
    month : int | None = None
    day : int | None = None

class AbsenResponse(BaseModel):
    msg: str
    data: dict[str, list[MoreAbsen]]