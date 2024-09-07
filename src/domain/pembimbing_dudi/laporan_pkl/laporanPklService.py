from operator import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import joinedload

# models
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from ....models.laporanPklModel import LaporanPKL

# common
from ....error.errorHandling import HttpException
import math

# async def addLaporanPkl(id_pembimbing_dudi : int,id_dudi : int,laporan : LaporanPklDudiBase,session : AsyncSession) -> LaporanPklDudiBase :
#     laporanPkl, file = laporan
#     laporanPklDict = laporanPkl.__dict__ 

