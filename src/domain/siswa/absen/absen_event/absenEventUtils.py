from fastapi import UploadFile
from.....error.errorHandling import HttpException
from ..radius_absen.radiusAbsenService import cekRadiusAbsen
from datetime import date
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload
from .....models.absenModel import Absen
from python_random_strings import random_strings
import os
import aiofiles

from sqlalchemy.ext.asyncio import AsyncSession
async def validateRadius(id_dudi : int,radius,session : AsyncSession,isIzin : bool) :
    radius = await cekRadiusAbsen(id_dudi,radius,session)
    print(radius)
    if not radius["data"]["inside_radius"] :
        if not isIzin :
            raise HttpException(400,"anda berada di luar radius")
        return False
    return True
    
async def validateAbsen(id_siswa : int,dateNow : date,session : AsyncSession) -> Absen :
    # find absen siswa today
    findAbsen : Absen = (await session.execute(select(Absen).options(joinedload(Absen.jadwal_absen)).where(and_(Absen.id_siswa == id_siswa,Absen.tanggal == dateNow)))).scalar_one_or_none()

    if not findAbsen :
        raise HttpException(400,"tidak ada jadwal absen pada hari ini")

    return findAbsen


IMAGE_STORE = os.getenv("DEV_IMAGE_ABSEN_STORE")
IMAGE_BASE_URL = os.getenv("DEV_IMAGE_ABSEN_BASE_URL")
async def save_image(file : UploadFile) -> str :
    ext_file = file.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{file.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{IMAGE_STORE}{file_name}"

    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(file.file.read())
        fileURl = f"{IMAGE_BASE_URL}/{file_name}"
        return fileURl
    
DOKUMEN_STORE = os.getenv("DEV_DOKUMEN_ABSEN_STORE")
DOKUMEN_BASE_URL = os.getenv("DEV_DOKUMEN_ABSEN_BASE_URL")
async def save_dokumen(file : UploadFile) -> str :
    ext_file = file.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg","pdf","docx","doc"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{file.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{DOKUMEN_STORE}{file_name}"

    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(file.file.read())
        fileURl = f"{DOKUMEN_BASE_URL}/{file_name}"
        return fileURl