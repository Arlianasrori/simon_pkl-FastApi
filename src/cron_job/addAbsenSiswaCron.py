from sqlalchemy import select, and_

# models
from ..db.db import SessionLocal
from  ..models.absenModel import Absen,AbsenJadwal,HariAbsen,HariEnum
from ..models.siswaModel import Siswa,StatusPKLEnum

# common
from ..domain.siswa.absen.absen_utils.dayUtils import get_day
from datetime import datetime, time
from python_random_strings import random_strings

async def addAbsenSiswaCron() :
    try : 
        session = SessionLocal()
        dateNow = datetime.now().date()

        findAllSiswa = (await session.execute(select(Siswa))).scalars().all()
        absesListForaddAll = []

        for siswa in findAllSiswa :
            print(siswa.__dict__)
            if siswa.id_dudi and siswa.status == StatusPKLEnum.sudah_pkl :
                # get jadwal for today with datenow
                findJadwalAbsenToday = (await session.execute(select(AbsenJadwal).where(and_(AbsenJadwal.id_dudi == siswa.id_dudi,AbsenJadwal.tanggal_mulai <= dateNow,AbsenJadwal.tanggal_berakhir >= dateNow)))).scalar_one_or_none()

                # jika tidak ada jadwal absen untuk hari ini
                if not findJadwalAbsenToday :
                    continue
                
                # findAbsen jika sudah ada absen 
                findAbsenNow = (await session.execute(select(Absen).where(and_(Absen.id_siswa == siswa.id,Absen.tanggal == dateNow)))).scalar_one_or_none()

                if findAbsenNow :
                    continue
                # lanjut validate
                dayNow : HariEnum = await get_day()

                # find jadwal hari ini
                findHariAbsenNow = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findJadwalAbsenToday.id,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()
                
                if not findHariAbsenNow :
                    continue

                absenMapping = {
                    "id" : random_strings.random_digits(6),
                    "id_absen_jadwal" : findHariAbsenNow.id_jadwal,
                    "id_siswa" : siswa.id,
                    "tanggal" : dateNow,
                    "absen_masuk" : None,
                    "absen_pulang" : None,
                    "status_absen_masuk" : None,
                    "status_absen_pulang" : None,
                    "foto_absen_masuk" : None,
                    "foto_absen_pulang" : None
                }

                absesListForaddAll.append(Absen(**absenMapping))
        session.add_all(absesListForaddAll)
        await session.commit()
    except Exception as err :
        print(err)
    finally :
        await session.close()