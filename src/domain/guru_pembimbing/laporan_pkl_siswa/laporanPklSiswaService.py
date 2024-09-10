from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.laporanPklModel import LaporanSiswaPKL
from ...models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase
from ....models.siswaModel import Siswa
from .laporanPklSiswaModel import ResponselaporanPklSiswaPag

# common
from ....error.errorHandling import HttpException
import math

async def getAllLaporanPklSiswa(id_guru : int,id_sekolah : int,page : int | None,session : AsyncSession) -> list[LaporanPklSiswaBase] | ResponselaporanPklSiswaPag :
    statementSelectLaporanPklSiswa = select(LaporanSiswaPKL).options(joinedload(LaporanSiswaPKL.siswa),joinedload(LaporanSiswaPKL.dudi)).where(and_(LaporanSiswaPKL.id_sekolah == id_sekolah,LaporanSiswaPKL.id_guru_pembimbing == id_guru))

    if page is not None :
        findLaporan = (await session.execute(statementSelectLaporanPklSiswa.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(LaporanSiswaPKL.id))).scalar_one()
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
        findLaporan = (await session.execute(statementSelectLaporanPklSiswa)).scalars().all()
        return {
            "msg" : "success",
            "data" : findLaporan
        }

async def getLaporanPklSiswaById(id_laporan : int,id_guru : int,session : AsyncSession) -> LaporanPklSiswaBase :
    findLaporan = (await session.execute(select(LaporanSiswaPKL).where(and_(LaporanSiswaPKL.id == id_laporan,LaporanSiswaPKL.siswa.has(Siswa.id_guru_pembimbing == id_guru))))).scalar_one()
    if not findLaporan :
        raise HttpException(404,"laporan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }

