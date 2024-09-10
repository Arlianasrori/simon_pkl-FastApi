from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.laporanPklModel import LaporanPKL
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from .laporanPklDudiModel import ResponseLaporanPklDudiPag
from ....models.siswaModel import Siswa

# common
from ....error.errorHandling import HttpException
import math

async def getAllLaporanPklSiswa(id_guru : int,id_sekolah : int,page : int | None,session : AsyncSession) -> list[LaporanPklDudiBase] | ResponseLaporanPklDudiPag :
    statementSelectLaporanPklDudi = select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi)).where(and_(LaporanPKL.id_sekolah == id_sekolah,LaporanPKL.id_guru_pembimbing == id_guru))

    if page is not None :
        findLaporan = (await session.execute(statementSelectLaporanPklDudi.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(LaporanPKL.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findLaporan,
                "count_data" : len(findLaporan),
                "count_page" : countPage
            }
        } 
    else :
        findLaporan = (await session.execute(statementSelectLaporanPklDudi)).scalars().all()
        return {
            "msg" : "success",
            "data" : findLaporan
        }

async def getLaporanPklSiswaById(id_laporan : int,id_guru : int,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporan = (await session.execute(select(LaporanPKL).where(and_(LaporanPKL.id == id_laporan,LaporanPKL.siswa.has(Siswa.id_guru_pembimbing == id_guru))))).scalar_one()
    if not findLaporan :
        raise HttpException(404,"laporan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }

