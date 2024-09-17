from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,extract
from sqlalchemy.orm import joinedload

# models
from .getAbsenModel import FilterAbsen,MoreAbsen
from ....models_domain.absen_model import MoreAbsen
from .....models.absenModel import Absen

# common
from .....error.errorHandling import HttpException
from datetime import datetime,timedelta

async def getAllAbsen(id_siswa : int,filter : FilterAbsen,isSevenDay : bool,session : AsyncSession) -> list[MoreAbsen] :
    seven_days_ago = datetime.now() - timedelta(days=7)

    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa),joinedload(Absen.keterangan_absen_masuk),joinedload(Absen.keterangan_absen_pulang))
        .where(and_(
        Absen.id_siswa == id_siswa,
        Absen.tanggal >= seven_days_ago if isSevenDay else True,
        extract('year', Absen.tanggal) == filter.year if filter.year else True,
        extract('month', Absen.tanggal) == filter.month if filter.month else True,
        extract('day', Absen.tanggal) == filter.day if filter.day else True
        )).order_by(desc(Absen.tanggal)))).scalars().all()
    
    return {
        "msg" : "success",
        "data" : findAbsen
    }

async def getAbsenById(id_absen : int,id_siswa : int,session : AsyncSession) -> MoreAbsen :
    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa),joinedload(Absen.keterangan_absen_masuk),joinedload(Absen.keterangan_absen_pulang)).where(and_(Absen.id == id_absen,Absen.id_siswa == id_siswa)))).scalar_one_or_none()

    if not findAbsen :
        raise HttpException(404,"absen tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findAbsen
    }