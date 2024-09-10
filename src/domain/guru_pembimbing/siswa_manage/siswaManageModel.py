from ...models_domain.common_model import PaginationBase
from ...models_domain.siswa_model import SiswaWithDudi

class ResponseSiswaPag(PaginationBase) :
    data : list[SiswaWithDudi] = []