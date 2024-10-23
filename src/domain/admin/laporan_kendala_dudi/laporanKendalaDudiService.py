from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload

# models
from ....models.laporanPklModel import LaporanKendalaDudi
from ...models_domain.laporan_kendala_dudi_model import LaporanKendalaDudiWithSiswaPembimbingDudi
from .laporanKendalaDudiModel import FilterLaporanPklKendalaDudiQuery,ResponseLaporanPklDudiPag
from ....models.siswaModel import Siswa
from ....models.pembimbingDudiModel import PembimbingDudi

# common
from ....error.errorHandling import HttpException
import datetime
import math

async def getAllLaporanKendalaDudi(id_sekolah : int,id_tahun : int,page : int, query : FilterLaporanPklKendalaDudiQuery,session : AsyncSession) -> ResponseLaporanPklDudiPag :
    if query.month or query.year:
        now = datetime.datetime.now()
        startQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 1, 1)
        endQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 12, 31)
        print(startQuery)

    selectStatement = select(LaporanKendalaDudi).options(joinedload(LaporanKendalaDudi.siswa).joinedload(Siswa.dudi),joinedload(LaporanKendalaDudi.pembimbingDudi)).where(and_(and_(LaporanKendalaDudi.tanggal >= startQuery, LaporanKendalaDudi.tanggal <= endQuery)) if query.month else True, LaporanKendalaDudi.tanggal == query.tanggal if query.tanggal else True, LaporanKendalaDudi.pembimbingDudi.has(id_sekolah == id_sekolah), LaporanKendalaDudi.id_siswa == query.id_siswa if query.id_siswa else True,LaporanKendalaDudi.pembimbingDudi.has(Siswa.id_tahun == id_tahun))
    
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

async def getLaporanKendalaById(id_laporan : int,id_sekolah : int,session : AsyncSession) -> LaporanKendalaDudiWithSiswaPembimbingDudi :
    findLaporan = (await session.execute(select(LaporanKendalaDudi).options(joinedload(LaporanKendalaDudi.siswa).joinedload(Siswa.dudi),joinedload(LaporanKendalaDudi.pembimbingDudi)).where(and_(LaporanKendalaDudi.id == id_laporan,LaporanKendalaDudi.pembimbingDudi.has(PembimbingDudi.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findLaporan :
        raise HttpException(404,"laporan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }

