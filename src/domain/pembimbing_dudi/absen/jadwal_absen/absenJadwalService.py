from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_
from sqlalchemy.orm import joinedload,subqueryload


# models 
from .absenJadwalModel import AddJadwalAbsenBody,UpdateJadwalAbsenBody
from .....models.absenModel import AbsenJadwal,HariAbsen
from ....models_domain.absen_model import JadwalAbsenWithHari

# common
from copy import deepcopy
from .....error.errorHandling import HttpException
from python_random_strings import random_strings
from .absenJadwalUtils import cek_hari_absen,get_date_difference_in_days
from .....utils.updateTable import updateTable
from datetime import date

# jadwal absen
async def addJadwalAbsen(id_dudi : int,jadwal : AddJadwalAbsenBody,session : AsyncSession) -> JadwalAbsenWithHari :
    if jadwal.tanggal_mulai > jadwal.tanggal_berakhir :
        raise HttpException(400,"keselahan dalam memasukkan tanggal,harap periksa kembali")
    
    findCekJadwal = (await session.execute(select(AbsenJadwal).where(and_(AbsenJadwal.id_dudi == id_dudi,AbsenJadwal.tanggal_berakhir >= jadwal.tanggal_mulai)))).scalar_one_or_none()

    if findCekJadwal :
        raise HttpException(400,"tanggal pada jadwal telah ditetapkan pada jadwal lain,mohon untuk mengecek kembali jadwal yang ada")
    
    jadwalMapping = jadwal.model_dump(exclude={"hari"})
    date_mulai = date.fromisoformat(str(jadwal.tanggal_mulai))
    date_berakhir = date.fromisoformat(str(jadwal.tanggal_berakhir))

    selish_jadwal = get_date_difference_in_days(date_mulai,date_berakhir)
    jadwalMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi,"selisih_tanggal_day" : selish_jadwal})

    hari = await cek_hari_absen(jadwalMapping["id"],jadwal.hari)
    session.add(AbsenJadwal(**jadwalMapping))
    session.add_all(hari["hari"])
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : {
            **jadwalMapping,
            "hari" : hari["response"]
        }
    }


async def getAllJadwalAbsen(id_dudi : int,session : AsyncSession) -> list[JadwalAbsenWithHari] :
    findJadwal = (await session.execute(select(AbsenJadwal).where(AbsenJadwal.id_dudi == id_dudi).options(subqueryload(AbsenJadwal.hari)).order_by(desc(AbsenJadwal.tanggal_mulai)))).scalars().all() 

    return {
        "msg" : "success",
        "data" : findJadwal 
    }

async def getJadwalById(id_jadwal : int,id_dudi : int,session : AsyncSession) -> JadwalAbsenWithHari :
    findJadwal = (await session.execute(select(AbsenJadwal).where(and_(AbsenJadwal.id == id_jadwal,AbsenJadwal.id_dudi == id_dudi)).options(subqueryload(AbsenJadwal.hari)))).scalar_one_or_none()

    if not findJadwal :
        raise HttpException(404,"jadwal absen tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findJadwal
    }

async def UpdateJadwalAbsen(id_jadwal : int,id_dudi : int,jadwal : UpdateJadwalAbsenBody,session : AsyncSession) -> JadwalAbsenWithHari :
    findJadwal = (await session.execute(select(AbsenJadwal).options(subqueryload(AbsenJadwal.hari)).where(and_(AbsenJadwal.id == id_jadwal,AbsenJadwal.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findJadwal :
        raise HttpException(404,"jadwal absen tidak ditemukan")
    if jadwal.tanggal_mulai and jadwal.tanggal_berakhir :
        if jadwal.tanggal_mulai > jadwal.tanggal_berakhir :
            raise HttpException(400,"keselahan dalam memasukkan tanggal,harap periksa kembali")

    if jadwal.model_dump(exclude_unset=True):
        print("masuk")
        updateTable(jadwal.model_dump(exclude={"hari"}),findJadwal)
    
    hariResponseList = []
    jadwalDictCopy = deepcopy(findJadwal.__dict__)

    if jadwal.hari :
        for hari in jadwal.hari :
            findHari = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id == hari.id,HariAbsen.id_jadwal == id_jadwal)))).scalar_one_or_none()

            if not findHari :
                raise HttpException(400,"hari tidak ditemukan")
            
            if hari.batas_absen_masuk : 
                if hari.batas_absen_masuk > hari.batas_absen_pulang :
                    raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")
            
            if hari.batas_absen_masuk and hari.batas_absen_pulang :
                if hari.batas_absen_masuk > hari.batas_absen_pulang :
                    raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")

            updateTable(hari,findHari)
            hariResponseList.append(findHari.__dict__.copy())
    
    return {
        "msg" : "success",
        "data" : {
            **jadwalDictCopy,
            "hari" : hariResponseList

        }
    }

        
async def deleteJadwalAbsen(id_jadwal : int,id_dudi : int,session : AsyncSession) -> JadwalAbsenWithHari:
    findJadwal = (await session.execute(select(AbsenJadwal).options(subqueryload(AbsenJadwal.hari)).where(and_(AbsenJadwal.id == id_jadwal,AbsenJadwal.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findJadwal :
        raise HttpException(404,"jadwal absen tidak ditemukan")
    
    jadwalDictCopy = deepcopy(findJadwal.__dict__)

    await session.delete(findJadwal)
    await session.commit()
    return {
        "msg" : "success",
        "data" : jadwalDictCopy
    }