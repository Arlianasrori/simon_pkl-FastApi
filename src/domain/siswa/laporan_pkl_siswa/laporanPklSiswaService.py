from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func,extract
from sqlalchemy.orm import joinedload

# models
from ...models_domain.laporan_pkl_siswa_model import LaporanPklSiswaBase,LaporanPklWithoutDudiAndSiswa
from ....models.laporanPklModel import LaporanSiswaPKL
from .laporanPklSiswaModel import AddLaporanPklSiswaBody,UpdateLaporanPklSiswaBody,ResponseGetLaporanPklSiswaPag,FilterLaporan

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

async def addLaporanPklSiswa(id_siswa : int,id_dudi : int,laporan : AddLaporanPklSiswaBody,session : AsyncSession) -> LaporanPklWithoutDudiAndSiswa :
    if not id_dudi :
        raise HttpException(400,f"siswa belum memiliki tempat pkl")

    laporanMapping = laporan.model_dump()
    laporanMapping.update({"id" : random_strings.random_digits(6),"id_siswa":id_siswa,"id_dudi":id_dudi})
    
    session.add(LaporanSiswaPKL(**laporanMapping))

    await session.commit()
    return {
        "msg" : "successs",
        "data" : laporanMapping
    }


FILE_LAPORAN_STORE = os.getenv("DEV_LAPORAN_PKL_SISWA")
FILE_LAPORAN_BASE_URL = os.getenv("DEV_LAPORAN_PKL_SISWA_BASE_URL")
async def addUpdateFileLaporanPkl(id_siswa : int,id_laporan_pkl : int,file : UploadFile,session : AsyncSession) -> LaporanPklWithoutDudiAndSiswa :
    findLaporanPkl = (await session.execute(select(LaporanSiswaPKL).where(and_(LaporanSiswaPKL.id == id_laporan_pkl,LaporanSiswaPKL.id_siswa == id_siswa)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")

    ext_file = file.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg","pdf","docx","doc","xls","xlsx"] :
        raise HttpException(400,f"format file tidak di dukung")

    file_name = f"{random_strings.random_digits(12)}-{file.filename.split(' ')[0]}.{ext_file[-1]}"
    
    file_name_save = f"{FILE_LAPORAN_STORE}{file_name}"
    fotoProfileBefore = findLaporanPkl.dokumentasi

    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(file.file.read())
        findLaporanPkl.dokumentasi = f"{FILE_LAPORAN_BASE_URL}/{file_name}"
    
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

async def updateLaporanPklSiswa(id_siswa : int,id_laporan_pkl : int,laporan : UpdateLaporanPklSiswaBody,session : AsyncSession) -> LaporanPklWithoutDudiAndSiswa :
    findLaporanPkl = (await session.execute(select(LaporanSiswaPKL).where(and_(LaporanSiswaPKL.id == id_laporan_pkl,LaporanSiswaPKL.id_siswa == id_siswa)))).scalar_one_or_none()

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

async def deleteLaporanPklSiswa(id_siswa : int,id_laporan_pkl : int,session : AsyncSession) -> LaporanPklWithoutDudiAndSiswa :
    findLaporanPkl = (await session.execute(select(LaporanSiswaPKL).where(and_(LaporanSiswaPKL.id == id_laporan_pkl,LaporanSiswaPKL.id_siswa == id_siswa)))).scalar_one_or_none()

    if not findLaporanPkl :
        raise HttpException(404,f"laporan pkl tidak ditemukan")
    
    fotoProfileBefore = deepcopy(findLaporanPkl.dokumentasi)
    await session.delete(findLaporanPkl)
    laporanPklDictCopy = deepcopy(findLaporanPkl.__dict__)
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

async def getAllLaporanPklSiswa(id_siswa : int,page : int,filter : FilterLaporan,session : AsyncSession) -> ResponseGetLaporanPklSiswaPag :
    findLaporan = (await session.execute(select(LaporanSiswaPKL).where(and_(LaporanSiswaPKL.id_siswa == id_siswa,extract('month', LaporanSiswaPKL.tanggal) == filter.month,extract('year', LaporanSiswaPKL.tanggal) == filter.year)).limit(10).offset(10 * (page - 1)))).scalars().all()
    countData = (await session.execute(select(func.count(LaporanSiswaPKL.id).filter(and_(LaporanSiswaPKL.id_siswa == id_siswa,extract('month', LaporanSiswaPKL.tanggal) == filter.month,extract('year', LaporanSiswaPKL.tanggal) == filter.year))))).scalar_one()
    countPage = math.ceil(countData / 10)

    return {
        "msg" : "success",
        "data" : {
            "data" : findLaporan,
            "count_data" : countData,
            "count_page" : countPage
        }
    }
    
async def getLaporanPklSiswaById(id_siswa : int,id_laporan : int,session : AsyncSession) -> LaporanPklSiswaBase :
    findLaporan = (await session.execute(select(LaporanSiswaPKL).options(joinedload(LaporanSiswaPKL.dudi),joinedload(LaporanSiswaPKL.siswa)).where(and_(LaporanSiswaPKL.id_siswa == id_siswa,LaporanSiswaPKL.id == id_laporan)))).scalar_one_or_none()
    
    if not findLaporan :
        raise HttpException(404,f"Laporan dengan id {id_laporan} tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findLaporan
    }