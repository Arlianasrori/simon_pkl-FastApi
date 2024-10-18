from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.laporanPklModel import LaporanSiswaPKL
from ...models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase
from ....models.siswaModel import Siswa
from .laporanPklSiswaModel import FilterBySiswa,LaporanResponse

# common
from ....error.errorHandling import HttpException
import math
from collections import defaultdict
from babel.dates import format_date
from babel import Locale

async def getAllLaporanPklSiswa(id_guru : int,id_sekolah : int,filter : FilterBySiswa,session : AsyncSession) -> list[LaporanPklSiswaBase] | LaporanResponse :
    statementSelectLaporanPklSiswa = select(LaporanSiswaPKL).options(joinedload(LaporanSiswaPKL.siswa),joinedload(LaporanSiswaPKL.dudi)).where(and_(LaporanSiswaPKL.siswa.has(Siswa.id_sekolah == id_sekolah),LaporanSiswaPKL.siswa.has(Siswa.id_guru_pembimbing == id_guru),LaporanSiswaPKL.id_siswa == filter.id_siswa if filter.id_siswa else True,LaporanSiswaPKL.siswa.has(Siswa.nama.ilike(f"%{filter.nama_siswa}%") if filter.nama_siswa else True)))

    
    findLaporan = (await session.execute(statementSelectLaporanPklSiswa)).scalars().all()

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

async def getLaporanPklSiswaById(id_laporan : int,id_guru : int,session : AsyncSession) -> LaporanPklSiswaBase :
    findLaporan = (await session.execute(select(LaporanSiswaPKL).where(and_(LaporanSiswaPKL.id == id_laporan,LaporanSiswaPKL.siswa.has(Siswa.id_guru_pembimbing == id_guru))))).scalar_one_or_none()
    if not findLaporan :
        raise HttpException(404,"laporan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }

