from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload

# models
from .laporanPklSiswaModel import ResponseLaporanPklSiswaPag,FilterLaporanPklSiswaQuery
from  ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from ....models.laporanPklModel import LaporanSiswaPKL
from ....models.sekolahModel import TahunSekolah
from ....models.siswaModel import Siswa

# common 
import math
import datetime
from ....error.errorHandling import HttpException

async def getAllLaporanPkl(page : int,id_sekolah : int,id_tahun : int,query : FilterLaporanPklSiswaQuery | None,session : AsyncSession) -> ResponseLaporanPklSiswaPag :
    findTahun = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == id_tahun))).scalar_one_or_none()

    if not findTahun :
        raise HttpException(404,"tahun tidak ditemukan")
    if query.month or query.year :
        now = datetime.datetime.now()
        startQuery = datetime.date(query.year if query.year else now.year,query.month if query.month else 1,1)
        endQuery = datetime.date(query.year if query.year else now.year,query.month if query.month else 12,31)
        print(startQuery)

    getLapoaran = (await session.execute(select(LaporanSiswaPKL).options(joinedload(LaporanSiswaPKL.siswa),joinedload(LaporanSiswaPKL.dudi)).where(and_(and_(LaporanSiswaPKL.tanggal >= startQuery,LaporanSiswaPKL.tanggal <= endQuery)) if query.month else True,LaporanSiswaPKL.tanggal == query.tanggal if query.tanggal else True,LaporanSiswaPKL.siswa.has(id_sekolah == id_sekolah),LaporanSiswaPKL.id_siswa == query.id_siswa if query.id_siswa else True).limit(10).offset(10 * (page - 1)))).scalars().all()

    conntData = (await session.execute(func.count(LaporanSiswaPKL.id))).scalar_one()
    countPage = math.ceil(conntData / 10)
    return {
        "msg" : "success",
        "data" : {
            "data" : getLapoaran,
            "count_data" : len(getLapoaran),
            "count_page" : countPage
        }
    }

async def getLaporanPkl(id_laporan : int,id_sekolah : int,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanSiswaPKL).options(joinedload(LaporanSiswaPKL.siswa),joinedload(LaporanSiswaPKL.dudi)).where(and_(LaporanSiswaPKL.id == id_laporan,LaporanSiswaPKL.siswa.has(Siswa.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,"laporan pkl tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporanPkl
    }