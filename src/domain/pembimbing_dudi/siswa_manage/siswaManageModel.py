from pydantic import BaseModel
from ...models_domain.common_model import PaginationBase
from ...models_domain.siswa_model import MoreSiswa

class ResponseSiswaPag(PaginationBase) :
    data : list[MoreSiswa] = []

class ResponseCountSiswa(BaseModel) :
    countSiswa : int

