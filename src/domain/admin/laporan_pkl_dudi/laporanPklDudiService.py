from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload

# models
from .laporanPklDudiModel import ResponseLaporanPklDudiPag,FilterLaporanPklDudiQuery
from  ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from ....models.laporanPklModel import LaporanPKL
from ....models.sekolahModel import TahunSekolah
from ....models.siswaModel import Siswa

# common 
import math
import datetime
from ....error.errorHandling import HttpException

async def getAllLaporanPkl(page : int,id_sekolah : int,id_tahun : int,query : FilterLaporanPklDudiQuery | None,session : AsyncSession) -> ResponseLaporanPklDudiPag :
    findTahun = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == id_tahun))).scalar_one_or_none()

    if not findTahun :
        raise HttpException(404,"tahun tidak ditemukan")
    if query.month or query.year :
        now = datetime.datetime.now()
        startQuery = datetime.date(query.year if query.year else now.year,query.month if query.month else 1,1)
        endQuery = datetime.date(query.year if query.year else now.year,query.month if query.month else 12,31)
        print(startQuery)

    getLapoaran = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(and_(and_(LaporanPKL.tanggal >= startQuery,LaporanPKL.tanggal <= endQuery)) if query.month else True,LaporanPKL.tanggal == query.tanggal if query.tanggal else True,LaporanPKL.siswa.has(Siswa.id_sekolah == id_sekolah),LaporanPKL.id_siswa == query.id_siswa if query.id_siswa else True).limit(10).offset(10 * (page - 1)))).scalars().all()

    conntData = (await session.execute(func.count(LaporanPKL.id))).scalar_one()
    countPage = math.ceil(conntData / 10)
    print(getLapoaran)
    return {
        "msg" : "success",
        "data" : {
            "data" : getLapoaran,
            "count_data" : len(getLapoaran),
            "count_page" : countPage
        }
    }

async def getLaporanPkl(id_laporan : int,id_sekolah : int,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(and_(LaporanPKL.id == id_laporan,LaporanPKL.siswa.has(Siswa.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,"laporan pkl tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporanPkl
    }