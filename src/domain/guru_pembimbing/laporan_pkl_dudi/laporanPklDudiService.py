from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.laporanPklModel import LaporanPKL
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from .laporanPklDudiModel import Filter,LaporanDudiResponse 
from ....models.siswaModel import Siswa

# common
from ....error.errorHandling import HttpException
import math
from collections import defaultdict
from babel.dates import format_date
from babel import Locale

async def getAllLaporanPklDudi(id_guru : int,id_sekolah : int,filter : Filter,session : AsyncSession) -> LaporanDudiResponse :
    print(filter)
    statementSelectLaporanPklDudi = select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(and_(LaporanPKL.siswa.has(Siswa.id_sekolah == id_sekolah),LaporanPKL.siswa.has(Siswa.id_guru_pembimbing == id_guru),LaporanPKL.id_dudi == filter.id_dudi if filter.id_dudi else True,LaporanPKL.id_siswa == filter.id_siswa if filter.id_siswa else True))

    findLaporan = (await session.execute(statementSelectLaporanPklDudi)).scalars().all()

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

async def getLaporanPklDudiById(id_laporan : int,id_guru : int,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporan = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(and_(LaporanPKL.id == id_laporan,LaporanPKL.siswa.has(Siswa.id_guru_pembimbing == id_guru))))).scalar_one_or_none()
    if not findLaporan :
        raise HttpException(404,"laporan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }

