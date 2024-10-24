from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.laporanPklModel import LaporanKendalaDudi
from ...models_domain.laporan_kendala_dudi_model import LaporanKendalaDudiWithSiswa,LaporanKendalaDudiWithSiswaPembimbingDudi
from .laporanKendalaDudiModel import Filter,LaporanKendalaDudiResponse 
from ....models.siswaModel import Siswa

# common
from ....error.errorHandling import HttpException
import math
from collections import defaultdict
from babel.dates import format_date
from babel import Locale

async def getAllLaporanKendalaDudi(id_guru : int,id_sekolah : int,filter : Filter,session : AsyncSession) -> LaporanKendalaDudiResponse :
    print(filter)
    statementSelectLaporanKendala = select(LaporanKendalaDudi).options(joinedload(LaporanKendalaDudi.siswa).joinedload(Siswa.dudi)).where(and_(LaporanKendalaDudi.siswa.has(Siswa.id_sekolah == id_sekolah),LaporanKendalaDudi.siswa.has(Siswa.id_guru_pembimbing == id_guru),LaporanKendalaDudi.siswa.has(Siswa.id_dudi == filter.id_dudi if filter.id_dudi else True),LaporanKendalaDudi.id_siswa == filter.id_siswa if filter.id_siswa else True))

    findLaporan = (await session.execute(statementSelectLaporanKendala)).scalars().all()

    grouped_laporan = defaultdict(list)
     # Membuat locale Indonesia
    locale_id = Locale('id', 'ID')
    for laporan in findLaporan:
        date_key = format_date(laporan.tanggal, format="EEEE, d MMMM yyyy", locale=locale_id)
        grouped_laporan[date_key].append(laporan)

    return {
        "msg" : "success",
        "data" : grouped_laporan
    }

async def getLaporanKendalaById(id_laporan : int,id_guru : int,session : AsyncSession) -> LaporanKendalaDudiWithSiswaPembimbingDudi :
    findLaporan = (await session.execute(select(LaporanKendalaDudi).options(joinedload(LaporanKendalaDudi.siswa).joinedload(Siswa.dudi),joinedload(LaporanKendalaDudi.pembimbingDudi)).where(and_(LaporanKendalaDudi.id == id_laporan,LaporanKendalaDudi.siswa.has(Siswa.id_guru_pembimbing == id_guru))))).scalar_one_or_none()

    if not findLaporan :
        raise HttpException(404,"laporan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }

