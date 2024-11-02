from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_
from sqlalchemy.orm import joinedload,subqueryload


# models 
from .absenJadwalModel import AddJadwalAbsenBody,UpdateJadwalAbsenBody,AddHariAbsen, UpdateHariAbsenBody
from .....models.absenModel import HariAbsen
from ....models_domain.absen_model import JadwalAbsenWithHari, HariAbsenBase, HariAbsenWithDudi

# common
from copy import deepcopy
from .....error.errorHandling import HttpException
from python_random_strings import random_strings
from .absenJadwalUtils import cek_hari_absen
from .....utils.updateTable import updateTable
from datetime import date

# jadwal absen
async def addJadwalAbsen(id_dudi : int,jadwal : AddHariAbsen,session : AsyncSession) -> list[HariAbsenBase] :
    findHariabsen = (await session.execute(select(HariAbsen).where(HariAbsen.id_dudi == id_dudi))).scalars().all()
    # if jadwal.tanggal_mulai > jadwal.tanggal_berakhir :
    #     raise HttpException(400,"keselahan dalam memasukkan tanggal,harap periksa kembali")
    
    # findCekJadwal = (await session.execute(select(AbsenJadwal).where(and_(AbsenJadwal.id_dudi == id_dudi,AbsenJadwal.tanggal_berakhir >= jadwal.tanggal_mulai)))).scalar_one_or_none()

    # if findCekJadwal :
    #     raise HttpException(400,"tanggal pada jadwal telah ditetapkan pada jadwal lain,mohon untuk mengecek kembali jadwal yang ada")
    
    # jadwalMapping = jadwal.model_dump(exclude={"hari"})

    # jadwalMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi})

    hari = await cek_hari_absen(id_dudi,jadwal,findHariabsen)
    # session.add(AbsenJadwal(**jadwalMapping))
    session.add_all(hari["hari"])
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : hari["response"]
    }


async def getAllJadwalAbsen(id_dudi : int,session : AsyncSession) -> list[HariAbsenWithDudi] :
    findJadwal = (await session.execute(select(HariAbsen).where(HariAbsen.id_dudi == id_dudi).options(joinedload(HariAbsen.dudi)))).scalars().all() 

    return {
        "msg" : "success",
        "data" : findJadwal 
    }

async def getJadwalById(id_dudi : int,id_hari : int,session : AsyncSession) -> HariAbsenWithDudi :
    findJadwal = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id_dudi == id_dudi, HariAbsen.id == id_hari)).options(joinedload(HariAbsen.dudi)))).scalar_one_or_none()

    if not findJadwal :
        raise HttpException(404,"jadwal absen tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findJadwal
    }

async def UpdateJadwalAbsen(id_dudi : int,hari : list[UpdateHariAbsenBody],session : AsyncSession) -> list[HariAbsenBase] :
    # find jadwal absen
    findJadwal = (await session.execute(select(HariAbsen).options(joinedload(HariAbsen.dudi)).where(HariAbsen.id_dudi == id_dudi))).scalars().all()

    if not findJadwal :
        raise HttpException(404,"jadwal absen tidak ditemukan")
    
    # # cek tanggal mulai lebih besar dari tanggal berakhir
    # if jadwal.tanggal_mulai and jadwal.tanggal_berakhir :
    #     if jadwal.tanggal_mulai > jadwal.tanggal_berakhir :
    #         raise HttpException(400,"keselahan dalam memasukkan tanggal,harap periksa kembali")

    # # cek jika jadwal ada dan update jadwal absen
    # if jadwal.model_dump(exclude_unset=True):
    #     updateTable(jadwal.model_dump(exclude={"hari"}),findJadwal)
    
    hariResponseList = [] ## for response to user
    # jadwalDictCopy = deepcopy(findJadwal.__dict__) ## copy so that no refresh db after commit later

    if hari :
        for hariItem in hari :
            if hariItem.id :
                # find hari absen
                findHari = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id == hariItem.id)))).scalar_one_or_none()

                if not findHari :
                    raise HttpException(400,"hari tidak ditemukan")
                
                # cek batas absen masuk dan pulang valid
                if hariItem.batas_absen_masuk : 
                    if hariItem.batas_absen_masuk > findHari.batas_absen_pulang :
                        raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")
                if hariItem.batas_absen_pulang :
                    if hariItem.batas_absen_pulang < findHari.batas_absen_masuk :
                        raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")
                if hariItem.batas_absen_masuk and hariItem.batas_absen_pulang :
                    if hariItem.batas_absen_masuk > hariItem.batas_absen_pulang :
                        raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")

                updateTable(hariItem,findHari)
                print(findHari.__dict__)
                hariResponseList.append(findHari.__dict__.copy())

    listAddHariForDb = []  
    
    if len(hari) > 0 :
        # looping hariItem on addHari pydantic model
        for addHariItem in hari :
            # cek apakah batas absen mauk lebih besar dari batas absen pulang
            if addHariItem.batas_absen_masuk > addHariItem.batas_absen_pulang :
                raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")              
            
            if addHariItem.batas_absen_masuk > addHariItem.batas_absen_pulang :
                raise HttpException(400,"keselahan dalam memasukkan waktu,harap periksa kembali")

            # cek apakah hari yang ingin ditambahkan sudah ada di database
            existInDb = next((hariDb for hariDb in findJadwal if hariDb.__dict__["hari"] == addHariItem.hari),None)

            if existInDb or addHariItem.hari == None:
                continue
            
            # mapping hari item and add property id and id_jadwal
            addHariItemMapping = addHariItem.model_dump()
            addHariItemMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi})

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
        "data" : hariResponseList
    }
      
async def deleteJadwalAbsen(id_jadwal : int,id_dudi : int,session : AsyncSession) -> HariAbsenBase:
    findJadwal = (await session.execute(select(HariAbsen).where(and_(HariAbsen.id == id_jadwal,HariAbsen.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findJadwal :
        raise HttpException(404,"jadwal absen tidak ditemukan")
    
    jadwalDictCopy = deepcopy(findJadwal.__dict__)

    await session.delete(findJadwal)
    await session.commit()
    return {
        "msg" : "success",
        "data" : jadwalDictCopy
    }