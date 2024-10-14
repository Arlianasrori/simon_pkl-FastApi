from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,extract
from sqlalchemy.orm import joinedload

# models
from .getAbsenModel import FilterAbsen,AbsenResponse
from ....models_domain.absen_model import MoreAbsen,MoreAbsenWithDokumenSakit,MoreAbsenWithDudiHariAbsen
from .....models.absenModel import Absen,AbsenJadwal,HariAbsen,HariEnum
from .....models.siswaModel import Siswa

# common
from .....error.errorHandling import HttpException
from datetime import datetime,timedelta
from babel.dates import format_date
from babel import Locale

async def getAllAbsen(id_siswa : int,filter : FilterAbsen,isThreeDay : bool,session : AsyncSession) -> list[MoreAbsen] | AbsenResponse:
    three_days_ago = datetime.now() - timedelta(days=3)
    print(id_siswa)

    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa),joinedload(Absen.keterangan_absen_masuk),joinedload(Absen.keterangan_absen_pulang))
        .where(and_(
        Absen.id_siswa == id_siswa,
        Absen.tanggal >= three_days_ago if isThreeDay else True,
        extract('year', Absen.tanggal) == filter.year if filter.year else True,
        extract('month', Absen.tanggal) == filter.month if filter.month else True,
        extract('day', Absen.tanggal) == filter.day if filter.day else True
        )).order_by(desc(Absen.tanggal)))).scalars().all()
    

    return {
        "msg" : "success",
        "data" : findAbsen
    }

async def getAbsenById(id_absen : int,id_siswa : int,session : AsyncSession) -> MoreAbsenWithDudiHariAbsen :  
    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa).joinedload(Siswa.dudi),joinedload(Absen.keterangan_absen_masuk),joinedload(Absen.keterangan_absen_pulang),joinedload(Absen.dokumenSakit),joinedload(Absen.jadwal_absen).options(joinedload(AbsenJadwal.dudi))).where(and_(Absen.id == id_absen,Absen.id_siswa == id_siswa)))).scalar_one_or_none()

    if not findAbsen :
        raise HttpException(404,"absen tidak ditemukan")
    
    locale_id = Locale('id', 'ID')
    date_key = format_date(findAbsen.tanggal, format="EEEE, d MMMM yyyy", locale=locale_id)
    day = date_key.split(" ")[0].split(",")[0]
    print(day)
    
    findHariAbsen = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findAbsen.id_absen_jadwal,HariAbsen.hari == day.lower())))).scalar_one_or_none()
    findAbsenDict = findAbsen.__dict__
    return {
        "msg" : "success",
        "data" : {
            **findAbsenDict,
            "jadwal_hari" : findHariAbsen
        }
    }