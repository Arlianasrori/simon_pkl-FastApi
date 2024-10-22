from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, and_
from sqlalchemy.orm import subqueryload


# models
from .absenJadwalModel import RadiusBody,ResponseCekAbsen,JenisAbsenEnum
from ....models_domain.absen_model import JadwalAbsenWithHari
from  .....models.absenModel import Absen,AbsenJadwal,HariAbsen,HariEnum
from ..radius_absen.radiusAbsenService import cekRadiusAbsen

# common
from .....error.errorHandling import HttpException
from ..absen_utils.zonaWaktu import get_timezone_from_coordinates,get_local_time
from ..absen_utils.dayUtils import get_day
from python_random_strings import random_strings
from .....utils.timeToFloat import time_to_float

async def getAllJadwalAbsen(id_dudi : int,session : AsyncSession) -> list[JadwalAbsenWithHari] :
    findJadwalAbsen = (await session.execute(select(AbsenJadwal).options(subqueryload(AbsenJadwal.hari)).where(AbsenJadwal.id_dudi == id_dudi).order_by(desc(AbsenJadwal.tanggal_mulai)))).scalars().all()

    return {
        "msg" : "success",
        "data" : findJadwalAbsen
    }

async def getJadwalAbsenById(id_dudi : int,id_jadwal : int,session : AsyncSession) -> JadwalAbsenWithHari :
    findJadwalAbsen = (await session.execute(select(AbsenJadwal).options(subqueryload(AbsenJadwal.hari)).where(and_(AbsenJadwal.id_dudi == id_dudi,AbsenJadwal.id == id_jadwal)))).scalar_one_or_none()

    if not findJadwalAbsen :
        raise HttpException(404,"Jadwal absen tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findJadwalAbsen
    }

async def cekAbsen(id_siswa : int,id_dudi : int | None,koordinat : RadiusBody,session : AsyncSession) -> ResponseCekAbsen :
    if id_dudi is None :
        raise HttpException(400,"siswa belum memiliki tempat pkl")

    # cek radius
    cekRadius = await cekRadiusAbsen(id_dudi,koordinat,session)

    # get time zone and datetime based on timezona
    zonaWaktu = await get_timezone_from_coordinates(koordinat.latitude,koordinat.longitude)
    now = await get_local_time(zonaWaktu)
    dateNow = now.date()
    timeNow = now.time()

    # get jadwal for today with datenow
    findJadwalAbsenToday = (await session.execute(select(AbsenJadwal).where(and_(AbsenJadwal.id_dudi == id_dudi,AbsenJadwal.tanggal_mulai <= dateNow,AbsenJadwal.tanggal_berakhir >= dateNow)))).scalar_one_or_none()

    # jika tidak ada jadwal absen untuk hari ini
    if not findJadwalAbsenToday :
        return {
            "msg" : "tidak ada jadwal absen untuk hari ini",
            "data" : {
                "canAbsen" : False
            }
        }
    
    # lanjut validate
    dayNow : HariEnum = await get_day()

    # find jadwal hari ini
    findHariAbsenNow = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findJadwalAbsenToday.id,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()

    # jika tidak ada jadwal absen untuk hari ini
    if not findHariAbsenNow :
        return {
            "msg" : "tidak ada jadwal absen untuk hari ini",
            "data" : {
                "canAbsen" : False,
                "jenis_absen" : None
            }
        }
    
    # find absen siswa pada hari ini,apakah berhasil dibuat oleh cron job atau tidak
    findAbsenSiswaToday = (await session.execute(select(Absen).where(and_(Absen.id_siswa == id_siswa,Absen.id_absen_jadwal == findJadwalAbsenToday.id,Absen.tanggal == dateNow)))).scalar_one_or_none()

    # validasi absen ketika absen siswa gagal dibuat oleh cron job
    if not findAbsenSiswaToday :
        # create absen for today
        absenMapping = {
            "id" : random_strings.random_digits(6),
            "id_absen_jadwal" : findJadwalAbsenToday.id,
            "id_siswa" : id_siswa,
            "tanggal" : dateNow,
            "absen_masuk" : None,
            "absen_pulang" : None,
            "status_absen_masuk" : None,
            "status_absen_pulang" : None,
            "foto_absen_masuk" : None,
            "foto_absen_pulang" : None
        }

        session.add(Absen(**absenMapping))       
        await session.commit()
        await session.refresh(findHariAbsenNow)

        # validasi ketika user belum melakukan absen masuk dan sudah melewati waktu absen pulang
        if timeNow > findHariAbsenNow.batas_absen_pulang :
                    return {
                        "msg" : "anda sudah melewati batas absen,anda dinyatakan tidak hadir hari ini",
                        "data" : {
                            "canAbsen" : False
                        }
                    }
        # validasi ketika user belum melakukan absen masuk dan sudah melewati batas absen masuk
        elif timeNow > findHariAbsenNow.batas_absen_masuk :
            return {
                "msg" : "anda sudah melewati batas absen masuk yang ditentukan,silahkan anda melakukan melakukan absen masuk dengan status telat untuk absen masuk",
                "data" : {
                    "canAbsen" : True,
                    "jenis_absen" : JenisAbsenEnum.TELAT
                }
            }
        # jika siswa belum melewati batas absen masuk
        else :
            return {
                "msg" : "silahkan melakukan absen masuk",
                "data" : {
                    "canAbsen" : True,
                    "jenis_absen" : JenisAbsenEnum.MASUK
                }
            }
    # validasi absen ketika absen siswa sudah dibuat pada cron job
    else :
        # handle jika siswa belum melakukan absen masuk
        if findAbsenSiswaToday.absen_masuk is None :
            # validasi jika user diluar radius
            if cekRadius["data"]["inside_radius"] is False :
                return {
                        "msg" : "anda belum melakukan absen masuk dan sedang berada diluar radius",
                        "data" : {
                            "canAbsen" : False,
                            "jenis_absen" : JenisAbsenEnum.MASUK,
                        }
                    }
            # validate jika waktu sekarang sudah melebihi batas absen masuk
            if timeNow > findHariAbsenNow.batas_absen_masuk :
                # validasi jika waktu telah melebihi batas absen pulang,siswa tidak dapat melakukan absen lagi untuk hari ini
                if timeNow > findHariAbsenNow.batas_absen_pulang :
                    return {
                        "msg" : "anda sudah melewati batas absen,anda dinyatakan tidak hadir hari ini",
                        "data" : {
                            "canAbsen" : False
                        }
                    }

                return {
                    "msg" : "anda sudah melewati batas absen masuk yang ditentukan,silahkan anda melakukan melakukan absen masuk dengan status telat untuk absen masuk",
                    "data" : {
                        "canAbsen" : True,
                        "jenis_absen" : JenisAbsenEnum.TELAT
                    }
                }
            # jika tidak telat
            else :
                return {
                "msg" : "silahkan melakukan absen masuk",
                "data" : {
                    "canAbsen" : True,
                    "jenis_absen" : JenisAbsenEnum.MASUK
                }
            }

        # handle jika siswa sudah melakukan absen masuk atau handle siswa untuk absen pulang
        else :
            # cek apakah siswa sudah melakukan absen pulang atau belum
            if findAbsenSiswaToday.absen_pulang :
                return {
                    "msg" : "anda sudah melakukan absen pulang",
                    "data" : {
                        "canAbsen" : False
                    }
                }
            # validasi jika user diluar radius
            if cekRadius["data"]["inside_radius"] is False :
                return {
                        "msg" : "anda belum melakukan absen pulang dan berada diluar radius,silahkan melakukan absen diluar radius untuk absen pulang",
                        "data" : {
                            "canAbsen" : True,
                            "jenis_absen" : JenisAbsenEnum.DILUAR_RADIUS
                        }
                    }
            # validasi jika user belum memenuhi batas minimum kerja
            timeNowFloat : float = await time_to_float(timeNow)
            absenMasukFloat : float = await time_to_float(findAbsenSiswaToday.absen_masuk)
            if timeNowFloat - absenMasukFloat < findHariAbsenNow.min_jam_absen :
                return {
                        "msg" : "anda belum memenuhi minimum waktu untuk melakukan absen pulang,silahkan melakukan izin absen jika ingin melakukan absen pulang",
                        "data" : {
                            "canAbsen" : False,
                            "jenis_absen" : JenisAbsenEnum.IZIN
                        }
                    }
            # validasi jika waktu sekarang sudah melebihi batas absen pulang
            elif timeNow > findHariAbsenNow.batas_absen_pulang :
                return {
                    "msg" : "anda sudah melewati batas absen pulang yang ditentukan, silahkan melakukan absen pulang dengan status telat",
                    "data" : {
                        "canAbsen" : True,
                        "jenis_absen" : JenisAbsenEnum.TELAT
                    }
                }
            # jika tidak telat
            else :
                return {
                        "msg" : "silahkan melakukan absen pulang",
                        "data" : {
                            "canAbsen" : True,
                            "jenis_absen" : JenisAbsenEnum.PULANG
                        }
                    }
            

async def getJadwalAbsenToday(id_siswa : int,id_dudi : int,koordinat : RadiusBody,session : AsyncSession) -> JadwalAbsenWithHari :
    # get time zone and datetime based on timezona
    zonaWaktu = await get_timezone_from_coordinates(koordinat.latitude,koordinat.longitude)
    now = await get_local_time(zonaWaktu)
    dateNow = now.date()

    # get jadwal absen for today
    findJadwalAbsenToday = (await session.execute(select(AbsenJadwal).where(and_(AbsenJadwal.id_dudi == id_dudi,AbsenJadwal.tanggal_mulai <= dateNow,AbsenJadwal.tanggal_berakhir >= dateNow)))).scalar_one_or_none()

    if not findJadwalAbsenToday :
        raise HttpException(404,"tidak ada jadwal absen untuk hari ini")

    dayNow : HariEnum = await get_day()

    # find jadwal hari ini
    findHariAbsenNow = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findJadwalAbsenToday.id,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()

    if not findHariAbsenNow :
        raise HttpException(404,"tidak ada jadwal absen untuk hari ini")
    
    jadwalDict = deepcopy(findJadwalAbsenToday.__dict__)
    hariAbsenDict = deepcopy(findHariAbsenNow.__dict__)

    return {
        "msg" : "success",
        "data" : {
            **jadwalDict,
            "hari" : hariAbsenDict
        }
    }