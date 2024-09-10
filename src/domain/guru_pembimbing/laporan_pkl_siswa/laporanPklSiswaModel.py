from ...models_domain.common_model import PaginationBase
from ...models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase

class ResponselaporanPklSiswaPag(PaginationBase) :
    data : list[LaporanPklSiswaBase] = []