from pydantic import BaseModel
from datetime import date as Date
from ...models_domain.absen_model import SiswaWithAbsen
from ...models_domain.common_model import PaginationBase
from ...models_domain.absen_model import StatusAbsenEnum

class ResponseAbsenPag(PaginationBase) :
    data : list[SiswaWithAbsen] = []

class FilterAbsenQuery(BaseModel) :
    id_siswa : int | None = None
    tanggal : Date | None = None
    month : int | None = None
    year : int | None = None
    status : StatusAbsenEnum | None = None
