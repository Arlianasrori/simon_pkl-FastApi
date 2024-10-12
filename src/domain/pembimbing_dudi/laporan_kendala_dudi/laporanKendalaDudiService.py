from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload

# models
from ...models_domain.laporan_kendala_dudi_model import LaporankendalaDudiBase, LaporanKendalaDudiWithSiswa
from ....models.laporanPklModel import LaporanKendalaDudi
from .laporanKendalaDudiModel import AddLaporanKendalaDudiBody,UpdateLaporanKendalaDudiBody
from ....models.siswaModel import Siswa
# common
from copy import deepcopy
import math
from ....error.errorHandling import HttpException
from python_random_strings import random_strings
import os
from ....utils.updateTable import updateTable
import aiofiles
from multiprocessing import Process
from ....utils.removeFile import removeFile

async def addLaporanPKLKendalaSiswa(id_pembimbing_dudi: int,laporan : AddLaporanKendalaDudiBody,session : AsyncSession) -> LaporankendalaDudiBase :
    laporanMapping = laporan.model_dump()
    laporanMapping.update({"id" : random_strings.random_digits(6),"id_pembimbing_dudi":id_pembimbing_dudi})
    
    session.add(LaporanKendalaDudi(**laporanMapping))

    await session.commit()
    return {
        "msg" : "successs",
        "data" : laporanMapping
    }


FILE_LAPORAN_STORE = os.getenv("DEV_LAPORAN_KENDALA_DUDI")
FILE_LAPORAN_BASE_URL = os.getenv("DEV_LAPORAN_KENDALA_DUDI_BASE_URL")
async def addUpdateFileLaporanKendala(id_pembimbing_dudi : int,id_laporan_pkl : int,file : UploadFile,session : AsyncSession) -> LaporankendalaDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanKendalaDudi).where(and_(LaporanKendalaDudi.id == id_laporan_pkl,LaporanKendalaDudi.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan kendala tidak ditemukan")

    ext_file = file.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg","pdf","docx","doc","xls","xlsx"] :
        raise HttpException(400,f"format file tidak di dukung")

    file_name = f"{random_strings.random_digits(12)}-{file.filename.split(' ')[0]}.{ext_file[-1]}"
    
    file_name_save = f"{FILE_LAPORAN_STORE}{file_name}"
    fotoProfileBefore = findLaporanPkl.file_laporan

    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(file.file.read())
        findLaporanPkl.file_laporan = f"{FILE_LAPORAN_BASE_URL}/{file_name}"
    
    if fotoProfileBefore :
        file_nama_db_split = fotoProfileBefore.split("/")
        file_name_db = file_nama_db_split[-1]
        os.remove(f"{FILE_LAPORAN_STORE}/{file_name_db}")
    
    laporanKendalaDictCopy = deepcopy(findLaporanPkl.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : laporanKendalaDictCopy
    }

async def updateLaporanKendala(id_pembimbing_dudi : int,id_laporan_pkl : int,laporan : UpdateLaporanKendalaDudiBody,session : AsyncSession) -> LaporankendalaDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanKendalaDudi).where(and_(LaporanKendalaDudi.id == id_laporan_pkl,LaporanKendalaDudi.id_siswa == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")
    
    if laporan.model_dump() != {} :
        updateTable(laporan,findLaporanPkl)

    laporanPklDictCopy = deepcopy(findLaporanPkl.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : laporanPklDictCopy
    }

async def deleteLaporanPklKendala(id_pembimbing_dudi : int,id_laporan_pkl : int,session : AsyncSession) -> LaporankendalaDudiBase :
    findLaporanKendala = (await session.execute(select(LaporanKendalaDudi).where(and_(LaporanKendalaDudi.id == id_laporan_pkl,LaporanKendalaDudi.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findLaporanKendala :
        raise HttpException(404,f"laporan pkl tidak ditemukan")
    
    # remove file from folder
    fotoProfileBefore = deepcopy(findLaporanKendala.file_laporan)
           
    await session.delete(findLaporanKendala)
    laporanKendalaDictCopy = deepcopy(findLaporanKendala.__dict__)
    await session.commit()
    if fotoProfileBefore :
        file_nama_db_split = fotoProfileBefore.split("/")
        file_name_db = file_nama_db_split[-1]

        proccess = Process(target=removeFile,args=(f"{FILE_LAPORAN_STORE}/{file_name_db}",))
        proccess.start()
    return {
        "msg" : "success",
        "data" : laporanKendalaDictCopy
    }
    


async def getAllLaporanKendala(id_pembimbing_dudi : int,session : AsyncSession) -> LaporankendalaDudiBase :
    findLaporan = (await session.execute(select(LaporanKendalaDudi).where(LaporanKendalaDudi.id_pembimbing_dudi == id_pembimbing_dudi))).scalars().all()

    return {
        "msg" : "success",
        "data" : findLaporan
    }
    
async def getLaporanKendalaById(id_pembimbing_dudi : int,id_laporan : int,session : AsyncSession) -> LaporanKendalaDudiWithSiswa :
    findLaporan = (await session.execute(select(LaporanKendalaDudi).options(joinedload(LaporanKendalaDudi.siswa).joinedload(Siswa.dudi),joinedload(LaporanKendalaDudi.pembimbingDudi)).where(and_(LaporanKendalaDudi.id_pembimbing_dudi == id_pembimbing_dudi,LaporanKendalaDudi.id == id_laporan)))).scalar_one_or_none()
    
    if not findLaporan :
        raise HttpException(404,f"Laporan kendala dengan id {id_laporan} tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }