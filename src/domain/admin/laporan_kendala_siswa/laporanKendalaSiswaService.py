from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.laporanPklModel import LaporanKendalaSiswa
from ...models_domain.laporan_kendala_model import LaporanKendalaWithSiswa
from .laporanKendalaSiswaModel import FilterLaporanPklKendalaSiswaQuery,ResponseLaporanKendalaSiswaPag
from ....models.siswaModel import Siswa

# common
from ....error.errorHandling import HttpException
import datetime
import math

async def getAllLaporanKendala(id_sekolah : int,id_tahun : int,page : int, query : FilterLaporanPklKendalaSiswaQuery,session : AsyncSession) -> ResponseLaporanKendalaSiswaPag :
    if query.month or query.year:
        now = datetime.datetime.now()
        startQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 1, 1)
        endQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 12, 31)
        print(startQuery)

    selectStatement = select(LaporanKendalaSiswa).options(joinedload(LaporanKendalaSiswa.siswa).joinedload(Siswa.dudi)).where(and_(and_(LaporanKendalaSiswa.tanggal >= startQuery, LaporanKendalaSiswa.tanggal <= endQuery)) if query.month else True, LaporanKendalaSiswa.tanggal == query.tanggal if query.tanggal else True, LaporanKendalaSiswa.siswa.has(id_sekolah == id_sekolah), LaporanKendalaSiswa.id_siswa == query.id_siswa if query.id_siswa else True,LaporanKendalaSiswa.siswa.has(Siswa.id_tahun == id_tahun))
    
    getLaporan = (await session.execute(selectStatement.limit(10).offset(10 * (page - 1)))).scalars().all()

    conntData = (await session.execute(selectStatement)).scalars().all()
    countPage = math.ceil(len(conntData) / 10)
    
    return {
        "msg": "success",
        "data": {
            "data": getLaporan,
            "count_data": len(getLaporan),
            "count_page": countPage
        }
    }

async def getLaporanKendalaById(id_laporan : int,id_sekolah : int, session : AsyncSession) -> LaporanKendalaWithSiswa :
    findLaporan = (await session.execute(select(LaporanKendalaSiswa).options(joinedload(LaporanKendalaSiswa.siswa).joinedload(Siswa.dudi)).where(and_(LaporanKendalaSiswa.id == id_laporan,LaporanKendalaSiswa.siswa.has(Siswa.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findLaporan :
        raise HttpException(404,"laporan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }

