from pydantic import BaseModel,field_validator
from ...models_domain.absen_model import AbsenWithSiswaDudi 
from babel.dates import format_date
from babel import Locale


class FilterAbsen(BaseModel) :
    year : int | None = None
    month : int | None = None
    day : int | None = None
    id_siswa : int | None = None
    nama : str | None = None

class AbsenResponse(AbsenWithSiswaDudi):
    tanggal : str
    @field_validator('tanggal',mode='before')
    def validate_tanggal(cls,v):
        locale_id = Locale('id', 'ID')
        return format_date(v, format="EEEE, d MMMM yyyy", locale=locale_id)
