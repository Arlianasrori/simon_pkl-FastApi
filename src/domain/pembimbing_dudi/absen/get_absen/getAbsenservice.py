from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,extract
from sqlalchemy.orm import joinedload

# models
from ....models_domain.absen_model import MoreAbsen
from .getAbsenModel import FilterAbsen,AbsenResponse
from .....models.absenModel import Absen
from .....models.siswaModel import Siswa

# common
from .....error.errorHandling import HttpException
from datetime import datetime,timedelta

async def getAllAbsen(id_dudi : int,filter : FilterAbsen,isSevenDay : bool,session : AsyncSession) -> AbsenResponse :
    seven_days_ago = datetime.now() - timedelta(days=7)

    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa).joinedload(Siswa.dudi))
        .where(and_(
        Absen.siswa.has(Siswa.id_dudi == id_dudi),
        Absen.tanggal >= seven_days_ago if isSevenDay else True,
        extract('year', Absen.tanggal) == filter.year if filter.year else True,
        extract('month', Absen.tanggal) == filter.month if filter.month else True,
        extract('day', Absen.tanggal) == filter.day if filter.day else True,
        Absen.siswa.has(Siswa.id == filter.id_siswa) if filter.id_siswa else True,
        Absen.siswa.has(Siswa.nama.like(f"%{filter.nama}%")) if filter.nama else True,
        )).order_by(desc(Absen.tanggal)))).scalars().all()
    
    absenDict: dict[str, list[Absen]] = {}
    for absen in findAbsen:
        tanggal_str = absen.tanggal.strftime("%Y-%m-%d")
        if tanggal_str not in absenDict:
            absenDict[tanggal_str] = []
        absenDict[tanggal_str].append(absen)
    
    return {
        "msg" : "success",
        "data" : absenDict
    }


async def getAbsenById(id_absen : int,id_dudi : int,session : AsyncSession)-> MoreAbsen :
    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa).joinedload(Siswa.dudi),joinedload(Absen.keterangan_absen_masuk),joinedload(Absen.keterangan_absen_pulang)).where(and_(Absen.id == id_absen,Absen.siswa.has(Siswa.id_dudi == id_dudi))))).scalar_one_or_none()

    if not findAbsen :
        raise HttpException(404,"absen tidak ditemukan")

    return {
        "msg" : "success",
        "data" : findAbsen
    }