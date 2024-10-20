import datetime
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

# models
from .absenEventModel import RadiusBody,IzinTelatAbsenEnum, ResponseAbsenIzinTelat
from ....models_domain.absen_model import AbsenBase,AbsenWithKeteranganPulang,MoreAbsen,AbsenWithDokumenSakit
from .....models.absenModel import Absen,HariAbsen,HariEnum,StatusAbsenEnum,StatusAbsenMasukKeluarEnum,StatusOtherAbsenEnum,IzinAbsenPulang,IzinAbsenMasuk,DokumenAbsenSakit

# common
from copy import deepcopy
from .....error.errorHandling import HttpException
from .absenEventUtils import validateRadius,validateAbsen,save_image,save_dokumen
from ..absen_utils.zonaWaktu import get_timezone_from_coordinates,get_local_time
from ..absen_utils.dayUtils import get_day
from .....utils.timeToFloat import time_to_float
from ..absen_utils.selisihTanggal import get_date_difference_in_days
from ..radius_absen.radiusAbsenService import cekRadiusAbsen
from python_random_strings import random_strings

# notification
from ...notification_siswa.notifUtils import runningProccessSyncAbsen,AddNotifAfterAbsen
from multiprocessing import Process

async def absenMasuk(id_siswa : int,id_dudi : int,radius : RadiusBody,image : UploadFile,session : AsyncSession) -> AbsenBase :   
    await validateRadius(id_dudi,radius,session)

    # get time zone and datetime based on timezona
    zonaWaktu = await get_timezone_from_coordinates(radius.latitude,radius.longitude)
    # if not zonaWaktu :
    #     raise HttpException(400,"anda berada diluar wilaya indonesia.Aplikasi saat ini hanya menukung penggunaan aplikasi diwilaya indonesia")

    # if not zonaWaktu :
    #     raise HttpException(400,"anda berada diluar indonesia")
    
    now = await get_local_time(zonaWaktu)
    dateNow = now.date()
    timeNow = now.time()

    findAbsenToday : Absen = await validateAbsen(id_siswa,dateNow,session)

    if not findAbsenToday.status_absen_masuk is None:
        raise HttpException(400,"anda telah melakukan absen masuk")
    
    dayNow : HariEnum = await get_day()

    # get hari absen hari ini
    findHariAbsenToday = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findAbsenToday.id_absen_jadwal,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()

    if not findHariAbsenToday :
        raise HttpException(400,"tidak ada jadwal absen hari ini")

    # gte selisih antara jadwal dengan waktu sekarang dan jadwal mulai dengan jadwal berakhir
    selisihTanggalAbsen = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,dateNow)
    selisihTanggalJadwal = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,findHariAbsenToday.jadwal.tanggal_berakhir)

    # validasi : jika selisih tanggal absen kurang dari 0 atau lebih dari selisih tanggal jadwal maka tanggal sudah melewati batas absen pada jadwal
    if selisihTanggalAbsen < 0 or selisihTanggalAbsen > selisihTanggalJadwal :
        raise HttpException(400,"tanggal absen tidak sesuai dengan jadwal")
    

    # jika telah melewati batas absen pulang
    if timeNow > findHariAbsenToday.batas_absen_pulang :
        raise HttpException(400,"anda telah melewati batas absen hari ini,anda dinyatakan tidak hadir")

    # jika telah melewati batas absen masuk,maka dinyatakn telat
    if timeNow > findHariAbsenToday.batas_absen_masuk :
        raise HttpException(400,"anda telah melewati batas absen masuk hari ini,silahkan melakukan absen telat dan menambah alasan anda telat pada absen telat")
    
    # update absen
    imageMasukUrl = await save_image(image)

    findAbsenToday.absen_masuk = timeNow
    findAbsenToday.status_absen_masuk = StatusAbsenMasukKeluarEnum.hadir.value
    findAbsenToday.status = StatusAbsenEnum.hadir.value
    findAbsenToday.foto_absen_masuk = imageMasukUrl

    absenTodayDictCopy = deepcopy(findAbsenToday.__dict__)
    await session.commit()

    proccess = Process(target=runningProccessSyncAbsen,args=(id_siswa,findAbsenToday.id,"masuk"))
    proccess.start()


    return {
        "msg" : "success",
        "data" : absenTodayDictCopy
    }

async def absenPulang(id_siswa : int,id_dudi : int,radius : RadiusBody,image : UploadFile,session : AsyncSession) -> AbsenBase :
    cekRadius = await cekRadiusAbsen(id_dudi,radius,session)

    if cekRadius["data"]["inside_radius"] is False :
        raise HttpException(400,"anda sedang berada diluar radius,silahkan melakukan absen diluar radius")
    # get time zone and datetime based on timezona
    zonaWaktu = await get_timezone_from_coordinates(radius.latitude,radius.longitude)

    # if not zonaWaktu :
    #     raise HttpException(400,"anda berada diluar indonesia")

    now = await get_local_time(zonaWaktu)
    dateNow = now.date()
    timeNow = now.time()

    findAbsenToday : Absen = await validateAbsen(id_siswa,dateNow,session)

    if findAbsenToday.status_absen_masuk is None or findAbsenToday.absen_masuk is None:
        raise HttpException(400,"anda belum melakukan absen masuk")

    if findAbsenToday.status_absen_pulang is not None:
        raise HttpException(400,"anda telah melakukan absen pulang")
 
    dayNow : HariEnum = await get_day()

    # get hari absen hari ini
    findHariAbsenToday = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findAbsenToday.id_absen_jadwal,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()

    if not findHariAbsenToday :
        raise HttpException(400,"tidak ada jadwal absen hari ini")
    
    # gte selisih antara jadwal dengan waktu sekarang dan jadwal mulai dengan jadwal berakhir
    selisihTanggalAbsen = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,dateNow)
    selisihTanggalJadwal = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,findHariAbsenToday.jadwal.tanggal_berakhir)

    # validasi : jika selisih tanggal absen kurang dari 0 atau lebih dari selisih tanggal jadwal maka tanggal sudah melewati batas absen pada jadwal
    if selisihTanggalAbsen < 0 or selisihTanggalAbsen > selisihTanggalJadwal :
        raise HttpException(400,"tanggal absen tidak sesuai dengan jadwal")
    

    timeNowFloat : float = await time_to_float(timeNow)
    absenMasukFloat : float = await time_to_float(findAbsenToday.absen_masuk)

    # validasi jika user belum memenuhi batas minimum kerja
    if timeNowFloat - absenMasukFloat < findHariAbsenToday.min_jam_absen :
        raise HttpException(400,"anda belum memenuhi minimum waktu untuk melakukan absen pulang,silahkan melakukan izin jika ingin melakukan absen pulang")
    
    # validasi apakah user telat dalam melakukan absen pulang
    if timeNow > findHariAbsenToday.batas_absen_pulang :
        raise HttpException(400,"anda telah melewati batas absen pulang hari ini,silahkan melakukan absen telat dan menambah alasan anda telat pada absen telat")
    
    imagePulangUrl = await save_image(image)
    
    findAbsenToday.absen_pulang = timeNow
    findAbsenToday.status_absen_pulang = StatusAbsenMasukKeluarEnum.hadir.value
    findAbsenToday.foto_absen_pulang = imagePulangUrl

    if findAbsenToday.status == StatusAbsenEnum.izin.value :
        findAbsenToday.status = StatusAbsenEnum.hadir.value

    absenTodayDictCopy = deepcopy(findAbsenToday.__dict__)
    await session.commit()

    proccess = Process(target=runningProccessSyncAbsen,args=(id_siswa,findAbsenToday.id,"pulang"))
    proccess.start()

    return {
        "msg" : "success",
        "data" : absenTodayDictCopy
    }


async def absenDiluarRadius(id_siswa : int,id_dudi : int,note : str,radius : RadiusBody,image : UploadFile,session : AsyncSession) -> AbsenWithKeteranganPulang:
    zonaWaktu = await get_timezone_from_coordinates(radius.latitude,radius.longitude)

    # if not zonaWaktu :
    #     raise HttpException(400,"anda berada diluar indonesia")
    
    now = await get_local_time(zonaWaktu)
    dateNow = now.date()
    timeNow = now.time()

    findAbsenToday : Absen = await validateAbsen(id_siswa,dateNow,session)

    if findAbsenToday.status_absen_masuk is None or findAbsenToday.absen_masuk is None:
        raise HttpException(400,"anda belum melakukan absen masuk")

    if findAbsenToday.status_absen_pulang is not None:
        raise HttpException(400,"anda telah melakukan absen pulang")
 
    dayNow : HariEnum = await get_day()

    # get hari absen hari ini
    findHariAbsenToday = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findAbsenToday.id_absen_jadwal,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()

    if not findHariAbsenToday :
        raise HttpException(400,"tidak ada jadwal absen hari ini")

    # gte selisih antara jadwal dengan waktu sekarang dan jadwal mulai dengan jadwal berakhir
    selisihTanggalAbsen = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,dateNow)
    selisihTanggalJadwal = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,findHariAbsenToday.jadwal.tanggal_berakhir)

    # validasi : jika selisih tanggal absen kurang dari 0 atau lebih dari selisih tanggal jadwal maka tanggal sudah melewati batas absen pada jadwal
    if selisihTanggalAbsen < 0 or selisihTanggalAbsen > selisihTanggalJadwal :
        raise HttpException(400,"tanggal absen tidak sesuai dengan jadwal")
    

    timeNowFloat : float = await time_to_float(timeNow)
    absenMasukFloat : float = await time_to_float(findAbsenToday.absen_masuk)

    # validasi jika user belum memenuhi batas minimum kerja
    if timeNowFloat - absenMasukFloat < findHariAbsenToday.min_jam_absen :
        raise HttpException(400,"anda belum memenuhi minimum waktu untuk melakukan absen pulang")
    
    imagePulangUrl = await save_image(image)
    
    findAbsenToday.absen_pulang = timeNow
    findAbsenToday.status_absen_pulang = StatusAbsenMasukKeluarEnum.diluar_radius.value
    findAbsenToday.foto_absen_pulang = imagePulangUrl

    keteranganAbsenPulangMapping = {
        "id" : random_strings.random_digits(6),
        "id_absen" : findAbsenToday.id,
        "note" : note,
        "inside_radius" : False,
        "status_izin" : StatusOtherAbsenEnum.diluar_radius.value
    } 

    session.add(IzinAbsenPulang(**keteranganAbsenPulangMapping))

    absenTodayDictCopy = deepcopy(findAbsenToday.__dict__)
    await session.commit()

    proccess = Process(target=runningProccessSyncAbsen,args=(id_siswa,findAbsenToday.id,"diluar radius"))
    proccess.start()

    return {
        "msg" : "absen diluar radius success",
        "data" : {
            **absenTodayDictCopy,
            "keterangan_absen_pulang" : keteranganAbsenPulangMapping
        }
    }

async def absenIzinTelat(id_siswa : int,id_dudi : int,note : str,statusIzin : IzinTelatAbsenEnum,radius : RadiusBody,image : UploadFile,session : AsyncSession) -> ResponseAbsenIzinTelat :
    statusRadius = await validateRadius(id_dudi,radius,session,True if statusIzin.value == IzinTelatAbsenEnum.IZIN.value else False)

    # get time zone and datetime based on timezona
    zonaWaktu = await get_timezone_from_coordinates(radius.latitude,radius.longitude)

    # if not zonaWaktu :
    #     raise HttpException(400,"anda berada diluar indonesia")
    now = await get_local_time(zonaWaktu)
    dateNow = now.date()
    timeNow = now.time()

    findAbsenToday : Absen = await validateAbsen(id_siswa,dateNow,session)
    
    dayNow : HariEnum = await get_day()

    # get hari absen hari ini
    findHariAbsenToday = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findAbsenToday.id_absen_jadwal,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()

    if not findHariAbsenToday :
        raise HttpException(400,"tidak ada jadwal absen hari ini")

    # gte selisih antara jadwal dengan waktu sekarang dan jadwal mulai dengan jadwal berakhir
    selisihTanggalAbsen = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,dateNow)
    selisihTanggalJadwal = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,findHariAbsenToday.jadwal.tanggal_berakhir)

    # validasi : jika selisih tanggal absen kurang dari 0 atau lebih dari selisih tanggal jadwal maka tanggal sudah melewati batas absen pada jadwal
    if selisihTanggalAbsen < 0 or selisihTanggalAbsen > selisihTanggalJadwal :
        raise HttpException(400,"tanggal absen tidak sesuai dengan jadwal")
    
    # jenis absen untuk notifikasi
    absenTypeForNotif = None
    # if user belum melakukan absen masuk atau handle izin telat pada absen masuk
    if not findAbsenToday.absen_masuk or not findAbsenToday.status_absen_masuk :
        # jika telah melewati batas absen pulang
        if timeNow > findHariAbsenToday.batas_absen_pulang :
            raise HttpException(400,"anda telah melewati batas absen hari ini,anda dinyatakan tidak hadir")
    
        imageMasukUrl = await save_image(image,True)
        findAbsenToday.absen_masuk = timeNow
        findAbsenToday.status_absen_masuk = statusIzin.value
        findAbsenToday.foto_absen_masuk = imageMasukUrl
        findAbsenToday.status = StatusAbsenEnum.izin.value if statusIzin == IzinTelatAbsenEnum.IZIN else StatusAbsenEnum.hadir.value

        keteranganAbsenMasukMapping = {
            "id" : random_strings.random_digits(6),
            "id_absen" : findAbsenToday.id,
            "note" : note,
            "inside_radius" : statusRadius,
            "status_izin" : statusIzin.value
        } 

        session.add(IzinAbsenMasuk(**keteranganAbsenMasukMapping))
        absenTypeForNotif = "masuk"
    # if user sudah melakukan absen masuk atau handle izin telat pada absen pulang   
    else :
        # if user telah melakukan absen pulang,atau menyelsaikan absen
        if findAbsenToday.status_absen_pulang or findAbsenToday.absen_pulang :
            raise HttpException(400,"anda telah melakukan absen pulang")
        
        timeNowFloat : float = await time_to_float(timeNow)
        absenMasukFloat : float = await time_to_float(findAbsenToday.absen_masuk)

        #  jika status izin telat validasi jika user belum memenuhi batas minimum kerja
        if statusIzin == IzinTelatAbsenEnum.TELAT :
            # validasi jika user belum memenuhi batas minimum kerja
            if timeNowFloat - absenMasukFloat < findHariAbsenToday.min_jam_absen :
                raise HttpException(400,"anda belum memenuhi minimum waktu untuk melakukan absen pulang,jika silahkan melakukan izin absen jika ingin melakukan absen pulang")
         
        imagePulangUrl = await save_image(image,True)
        findAbsenToday.absen_pulang = timeNow
        findAbsenToday.status_absen_pulang = statusIzin.value
        findAbsenToday.foto_absen_pulang = imagePulangUrl

        if statusIzin == IzinTelatAbsenEnum.TELAT :
            findAbsenToday.status = StatusAbsenEnum.hadir.value

        keteranganAbsenPulangMapping = {
            "id" : random_strings.random_digits(6),
            "id_absen" : findAbsenToday.id,
            "note" : note,
            "inside_radius" : statusRadius,
            "status_izin" : StatusOtherAbsenEnum.diluar_radius.value
        }

        session.add(IzinAbsenPulang(**keteranganAbsenPulangMapping))
        absenTypeForNotif = "pulang"

    id_absen = deepcopy(findAbsenToday.id)
    await session.commit()

    proccess = Process(target=runningProccessSyncAbsen,args=(id_siswa,id_absen,f"{statusIzin.value} untuk jenis absen {absenTypeForNotif}"))
    proccess.start()

    return {
        "msg" : "absen success"
    }

async def absenSakit(id_siswa : int,radius : RadiusBody,dokumen : UploadFile,note : str,session : AsyncSession) -> AbsenWithDokumenSakit :
    # get time zone and datetime based on timezona
    zonaWaktu = await get_timezone_from_coordinates(radius.latitude,radius.longitude)

    # if not zonaWaktu :
    #     raise HttpException(400,"anda berada diluar indonesia")

    now = await get_local_time(zonaWaktu)
    dateNow = now.date()

    findAbsenToday : Absen = await validateAbsen(id_siswa,dateNow,session)
    
    dayNow : HariEnum = await get_day()

    # get hari absen hari ini
    findHariAbsenToday = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_jadwal == findAbsenToday.id_absen_jadwal,HariAbsen.hari == dayNow.value)))).scalar_one_or_none()

    if not findHariAbsenToday :
        raise HttpException(400,"tidak ada jadwal absen hari ini")
    
    # gte selisih antara jadwal dengan waktu sekarang dan jadwal mulai dengan jadwal berakhir
    selisihTanggalAbsen = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,dateNow)
    selisihTanggalJadwal = await get_date_difference_in_days(findHariAbsenToday.jadwal.tanggal_mulai,findHariAbsenToday.jadwal.tanggal_berakhir)

    # validasi : jika selisih tanggal absen kurang dari 0 atau lebih dari selisih tanggal jadwal maka tanggal sudah melewati batas absen pada jadwal
    if selisihTanggalAbsen < 0 or selisihTanggalAbsen > selisihTanggalJadwal :
        raise HttpException(400,"tanggal absen tidak sesuai dengan jadwal")
    
    findAbsenToday.status = StatusAbsenEnum.sakit.value
    dokumenUrl = await save_dokumen(dokumen)

    absenSakitMapping = {
        "id" : random_strings.random_digits(6),
        "id_absen" : findAbsenToday.id,
        "dokumen" : dokumenUrl,
        "note" : note
    }

    session.add(DokumenAbsenSakit(**absenSakitMapping))

    absenTodayDictCopy = deepcopy(findAbsenToday.__dict__)
    await session.commit()

    proccess = Process(target=runningProccessSyncAbsen,args=(id_siswa,findAbsenToday.id,f"sakit"))
    proccess.start()

    return {
        "msg" : "absen sakit success",
        "data" : {
            **absenTodayDictCopy,
            "dokumenSakit" : absenSakitMapping
        }
    }