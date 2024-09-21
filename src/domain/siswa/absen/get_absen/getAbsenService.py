from fastapi.background import P
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,extract
from sqlalchemy.orm import joinedload

# models
from .getAbsenModel import FilterAbsen,AbsenResponse
from ....models_domain.absen_model import MoreAbsen
from .....models.absenModel import Absen

# common
from .....error.errorHandling import HttpException
from datetime import datetime,timedelta

async def getAllAbsen(id_siswa : int,filter : FilterAbsen,isSevenDay : bool,isGrouping : bool,session : AsyncSession) -> list[MoreAbsen] | AbsenResponse:
    seven_days_ago = datetime.now() - timedelta(days=7)
    print(id_siswa)

    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa),joinedload(Absen.keterangan_absen_masuk),joinedload(Absen.keterangan_absen_pulang))
        .where(and_(
        Absen.id_siswa == id_siswa,
        Absen.tanggal >= seven_days_ago if isSevenDay else True,
        extract('year', Absen.tanggal) == filter.year if filter.year else True,
        extract('month', Absen.tanggal) == filter.month if filter.month else True,
        extract('day', Absen.tanggal) == filter.day if filter.day else True
        )).order_by(desc(Absen.tanggal)))).scalars().all()
    
    if isGrouping :
        absenDict : dict[str,list[Absen]] = {}
        daysOnWeek = 7 # jumlah hari dalam seminggu
        countStart = 1 # mulai dari minggu 1
        for absen in findAbsen :
            # satu bulan ada 4 minggu,jika lenih dari 4 dihentikan
            if countStart > 4 :
                break
            # jika minggu tidak ada di dict
            if str(countStart) not in absenDict :
                absenDict[str(countStart)] = []

            # hitung tanggal mulai dan tanggal akhir
            startDate = datetime.now().date() - timedelta(days=countStart * daysOnWeek)
            endDate = datetime.now().date() - timedelta(days=(countStart - 1) * daysOnWeek)
            if not absen.tanggal > endDate :
                if absen.tanggal >= startDate and absen.tanggal <= endDate :
                    absenDict[str(countStart)].append(absen)
                else :
                    countStart += 1
                    if str(countStart) in absenDict :
                        absenDict[str(countStart)] = [absen]

        return {
            "msg" : "success",
            "data" : absenDict
        }
    else :
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