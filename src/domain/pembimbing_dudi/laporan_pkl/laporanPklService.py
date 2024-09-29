from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,and_
from sqlalchemy.orm import joinedload
from fastapi import UploadFile
# models
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase,LaporanPklDudiWithOut
from ....models.laporanPklModel import LaporanPKL
from .laporanPklModel import AddLaporanPklDudiBody,UpdateLaporanPklDudiBody
from ....models.siswaModel import Siswa

# common
from copy import deepcopy
from ....error.errorHandling import HttpException
import math
from python_random_strings import random_strings
import os
from ....utils.updateTable import updateTable
import aiofiles
from multiprocessing import Process
from ....utils.removeFile import removeFile


async def addLaporanPkl(id_pembimbing_dudi : int,id_dudi : int,laporan : AddLaporanPklDudiBody,session : AsyncSession) -> LaporanPklDudiBase :
    laporanPklMapping = laporan.model_dump()
    laporanPklMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi,"id_pembimbing_dudi" : id_pembimbing_dudi})

    findSiswa = (await session.execute(select(Siswa).where(and_(Siswa.id == laporanPklMapping["id_siswa"],Siswa.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findSiswa :
        raise HttpException(404,f"siswa tidak ditemukan")

    session.add(LaporanPKL(**laporanPklMapping))
    await session.commit()

    findLaporanPkl = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(LaporanPKL.id == laporanPklMapping["id"]))).scalar_one_or_none()

    return {
        "msg" : "success",
        "data" : findLaporanPkl
    }


FILE_LAPORAN_STORE = os.getenv("DEV_LAPORAN_PKL_DUDI")
FILE_LAPORAN_BASE_URL = os.getenv("DEV_LAPORAN_PKL_DUDI_BASE_URL")
async def addUpdateFileLaporanPkl(id_laporan_pkl : int,file : UploadFile,session : AsyncSession) -> LaporanPklDudiWithOut :
    findLaporanPkl = (await session.execute(select(LaporanPKL).where(LaporanPKL.id == id_laporan_pkl))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")

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
    
    laporanPklDictCopy = deepcopy(findLaporanPkl.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : laporanPklDictCopy
    }

async def getLaporanPkl(id_pembimbing_dudi : int,page : int | None,session : AsyncSession) -> list[LaporanPklDudiBase] :
    statementSelectlaporan = select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(LaporanPKL.id_pembimbing_dudi == id_pembimbing_dudi)
    
    if page :
        findLaporan = (await session.execute(statementSelectlaporan.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(LaporanPKL.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findLaporan,
                "count_data" : len(findLaporan),
                "count_page" : countPage
            }
        }
    else :
        findlaporan = (await session.execute(statementSelectlaporan)).scalars().all()
        return {
            "msg" : "success",
            "data" : findlaporan
        }

async def getLaporanPklById(id_laporan_pkl : int,id_pembimbing_dudi : int,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(and_(LaporanPKL.id == id_laporan_pkl,LaporanPKL.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporanPkl
    }

async def updateLaporanPkl(id_laporan_pkl : int,id_pembimbing_dudi : int,laporan : UpdateLaporanPklDudiBody,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(and_(LaporanPKL.id == id_laporan_pkl,LaporanPKL.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")
    
    if laporan != {} :
        updateTable(laporan,findLaporanPkl)
        
    laporanPklDictCopy = deepcopy(findLaporanPkl.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : laporanPklDictCopy
    }
    
async def deleteLaporanPkl(id_laporan_pkl : int,id_pembimbing_dudi : int,session : AsyncSession) -> LaporanPklDudiBase :
    findLaporanPkl = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.siswa),joinedload(LaporanPKL.dudi),joinedload(LaporanPKL.pembimbing_dudi)).where(and_(LaporanPKL.id == id_laporan_pkl,LaporanPKL.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")
    
    fotoProfileBefore = deepcopy(findLaporanPkl.file_laporan)
    laporanPklDictCopy = deepcopy(findLaporanPkl.__dict__)
    await session.delete(findLaporanPkl)
    await session.commit()

    if fotoProfileBefore :
        file_nama_db_split = fotoProfileBefore.split("/")
        file_name_db = file_nama_db_split[-1]

        proccess = Process(target=removeFile,args=(f"{FILE_LAPORAN_STORE}/{file_name_db}",))
        proccess.start()

    return {
        "msg" : "success",
        "data" : laporanPklDictCopy
    }