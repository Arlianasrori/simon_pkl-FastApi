from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,extract
from sqlalchemy.orm import joinedload

# models
from ...models_domain.absen_model import MoreAbsen,MoreAbsenSiswaDudi
from .absenModel import FilterAbsen,AbsenResponse,AbsenResponseFormat
from ....models.absenModel import Absen
from ....models.siswaModel import Siswa

# common
from ....error.errorHandling import HttpException
from datetime import datetime,timedelta
from babel.dates import format_date
from babel import Locale

async def getAllAbsen(id_guru : int,filter : FilterAbsen,isSevenDay : bool,session : AsyncSession) -> AbsenResponse :
    seven_days_ago = datetime.now() - timedelta(days=7)

    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa).joinedload(Siswa.dudi))
        .where(and_(
        Absen.siswa.has(Siswa.id_guru_pembimbing == id_guru),
        Absen.tanggal >= seven_days_ago if isSevenDay else True,
        extract('year', Absen.tanggal) == filter.year if filter.year else True,
        extract('month', Absen.tanggal) == filter.month if filter.month else True,
        extract('day', Absen.tanggal) == filter.day if filter.day else True,
        Absen.siswa.has(Siswa.id == filter.id_siswa) if filter.id_siswa else True,
        Absen.siswa.has(Siswa.nama.like(f"%{filter.nama}%")) if filter.nama else True,
        )).order_by(desc(Absen.tanggal)))).scalars().all()
    
    return {
        "msg" : "success",
        "data" : findAbsen
    }
    
async def getAllAbsenWithFormat(id_guru : int,filter : FilterAbsen,isSevenDay : bool,session : AsyncSession) -> AbsenResponseFormat :
    seven_days_ago = datetime.now() - timedelta(days=7)

    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa).options(joinedload(Siswa.dudi),joinedload(Siswa.jurusan),joinedload(Siswa.kelas),joinedload(Siswa.alamat)))
        .where(and_(
        Absen.siswa.has(Siswa.id_guru_pembimbing == id_guru),
        Absen.tanggal >= seven_days_ago if isSevenDay else True,
        extract('year', Absen.tanggal) == filter.year if filter.year else True,
        extract('month', Absen.tanggal) == filter.month if filter.month else True,
        extract('day', Absen.tanggal) == filter.day if filter.day else True,
        Absen.siswa.has(Siswa.id == filter.id_siswa) if filter.id_siswa else True,
        Absen.siswa.has(Siswa.nama.like(f"%{filter.nama}%")) if filter.nama else True,
        )).order_by(desc(Absen.tanggal)))).scalars().all()
    
    locale_id = Locale('id', 'ID')
    absenDict: dict[str, list[Absen]] = {}
    for absen in findAbsen:
        tanggal_str = format_date(absen.tanggal, format="EEEE, d MMMM yyyy", locale=locale_id)
        if tanggal_str not in absenDict:
            absenDict[tanggal_str] = []
        absenDict[tanggal_str].append(absen)
    
    return {
        "msg" : "success",
        "data" : absenDict
    }


async def getAbsenById(id_absen : int,id_guru : int,session : AsyncSession)-> MoreAbsenSiswaDudi :
    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa).joinedload(Siswa.dudi),joinedload(Absen.keterangan_absen_masuk),joinedload(Absen.keterangan_absen_pulang)).where(and_(Absen.id == id_absen,Absen.siswa.has(Siswa.id_guru_pembimbing == id_guru))))).scalar_one_or_none()

    if not findAbsen :
        raise HttpException(404,"absen tidak ditemukan")

    return {
        "msg" : "success",
        "data" : findAbsen
    }