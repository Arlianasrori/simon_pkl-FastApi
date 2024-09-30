from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_
from sqlalchemy.orm import joinedload,subqueryload


# models 
from .absenJadwalModel import AddJadwalAbsenBody,UpdateJadwalAbsenBody,AddHariAbsen
from .....models.absenModel import AbsenJadwal,HariAbsen
from ....models_domain.absen_model import JadwalAbsenWithHari

# common
from copy import deepcopy
from .....error.errorHandling import HttpException
from python_random_strings import random_strings
from .absenJadwalUtils import cek_hari_absen
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

    jadwalMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi})

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

async def UpdateJadwalAbsen(id_jadwal : int,id_dudi : int,jadwal : UpdateJadwalAbsenBody,addHari : list[AddHariAbsen],session : AsyncSession) -> JadwalAbsenWithHari :
    # find jadwal absen
    findJadwal = (await session.execute(select(AbsenJadwal).options(subqueryload(AbsenJadwal.hari)).where(and_(AbsenJadwal.id == id_jadwal,AbsenJadwal.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findJadwal :
        raise HttpException(404,"jadwal absen tidak ditemukan")
    
    # cek tanggal mulai lebih besar dari tanggal berakhir
    if jadwal.tanggal_mulai and jadwal.tanggal_berakhir :
        if jadwal.tanggal_mulai > jadwal.tanggal_berakhir :
            raise HttpException(400,"keselahan dalam memasukkan tanggal,harap periksa kembali")

    # cek jika jadwal ada dan update jadwal absen
    if jadwal.model_dump(exclude_unset=True):
        updateTable(jadwal.model_dump(exclude={"hari"}),findJadwal)
    
    hariResponseList = [] ## for response to user
    jadwalDictCopy = deepcopy(findJadwal.__dict__) ## copy so that no refresh db after commit later

    if jadwal.hari :
        for hari in jadwal.hari :
            # find hari absen
            findHari = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id == hari.id,HariAbsen.id_jadwal == id_jadwal)))).scalar_one_or_none()

            if not findHari :
                raise HttpException(400,"hari tidak ditemukan")
            
            # cek batas absen masuk dan pulang valid
            if hari.batas_absen_masuk : 
                if hari.batas_absen_masuk > findHari.batas_absen_pulang :
                    raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")
            if hari.batas_absen_pulang :
                if hari.batas_absen_pulang < findHari.batas_absen_masuk :
                    raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")
            if hari.batas_absen_masuk and hari.batas_absen_pulang :
                if hari.batas_absen_masuk > hari.batas_absen_pulang :
                    raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")

            updateTable(hari,findHari)
            hariResponseList.append(findHari.__dict__.copy())

    listAddHariForDb = []  
    print("sampaisini")    
    if len(addHari) > 0 :
        # looping hariItem on addHari pydantic model
        for addHariItem in addHari :
            # cek apakah batas absen mauk lebih besar dari batas absen pulang
            if addHariItem.batas_absen_masuk > addHariItem.batas_absen_pulang :
                raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")              
            
            if addHariItem.batas_absen_masuk > addHariItem.batas_absen_pulang :
                raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")

            # cek apakah hari yang ingin ditambahkan sudah ada di database
            existInDb = next((hariDb for hariDb in findJadwal.hari if hariDb.__dict__["hari"] == addHariItem.hari),None)

            if existInDb :
                raise HttpException(400,"error terdapat hari yang sama")
            
            # mapping hari item and add property id and id_jadwal
            addHariItemMapping = addHariItem.model_dump()
            addHariItemMapping.update({"id" : random_strings.random_digits(6),"id_jadwal" : id_jadwal})

            # add to list and add_all later
            listAddHariForDb.append(HariAbsen(**addHariItemMapping))

            # add to lis response
            hariResponseList.append(addHariItemMapping)
    
    # if list add hari for db is not empty
    if len(listAddHariForDb) > 0 :
        session.add_all(listAddHariForDb)
        await session.commit()

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