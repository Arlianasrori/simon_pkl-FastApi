from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from .laporanPklDudiModel import ResponseGetLaporanPklDudiPag
from ....models.laporanPklModel import LaporanPKL

# common
import math
from ....error.errorHandling import HttpException

async def getAllLaporanPklDudi(id_siswa : int,page : int | None,session : AsyncSession) -> ResponseGetLaporanPklDudiPag :
    findLaporan = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.dudi)).where(LaporanPKL.id_siswa == id_siswa).limit(10).offset(10 * (page - 1)))).scalars().all()
    
    countData = (await session.execute(select(func.count(LaporanPKL.id).filter(LaporanPKL.id_siswa == id_siswa)))).scalar_one()
    countPage = math.ceil(countData / 10)

    return {
        "msg" : "success",
        "data" : {
            "data" : findLaporan,
            "count_data" : countData,
            "count_page" : countPage
        }
    }

async def getLaporanPklDudiById(id_laporan_pkl : int,id_siswa : int,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi),joinedload(LaporanPKL.siswa)).where(and_(LaporanPKL.id == id_laporan_pkl,LaporanPKL.id_siswa == id_siswa)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporanPkl
    }