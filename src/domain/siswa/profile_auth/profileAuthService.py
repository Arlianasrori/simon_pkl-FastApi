import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload

# models
from ...models_domain.siswa_model import SiswaBase,DetailSiswa,SiswaWithAlamat
from ....models.dudiModel import Dudi
from ....models.siswaModel import Siswa,Jurusan,Kelas
from .profileAuthModel import UpdateProfileBody

# common
from copy import deepcopy
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable
from python_random_strings import random_strings
import os
from ....utils.sendOtp import sendOtp

async def getSiswa(id_siswa : int,session : AsyncSession) -> SiswaBase :
    findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id_siswa))).scalar_one_or_none()

    if not findSiswa :
        raise HttpException(404,"siswa tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findSiswa
    }

async def getProfileAuth(id_siswa : int,session : AsyncSession) -> DetailSiswa :
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.dudi).joinedload(Dudi.alamat),joinedload(Siswa.pembimbing_dudi),joinedload(Siswa.guru_pembimbing),joinedload(Siswa.kelas),joinedload(Siswa.jurusan),joinedload(Siswa.alamat)).where(Siswa.id == id_siswa))).scalar_one_or_none()

    if not findSiswa :
        raise HttpException(404,"siswa tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findSiswa
    }


async def updateProfile(id_siswa : int,siswa : UpdateProfileBody,session : AsyncSession) -> SiswaWithAlamat :
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.kelas),joinedload(Siswa.jurusan),joinedload(Siswa.alamat)).where(Siswa.id == id_siswa))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(400,f"Siswa dengan id {id_siswa} tidak ditemukan")
    
    if siswa.nis :
        findSiswaByNis = (await session.execute(select(Siswa).where(and_(Siswa.nis == siswa.nis,Siswa.id != id_siswa)))).scalar_one_or_none()
        if findSiswaByNis :
            raise HttpException(400,f"Siswa dengan NIS {siswa.nis} sudah ada")
    if siswa.id_jurusan :
        findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == siswa.id_jurusan))).scalar_one_or_none()
        if not findJurusan :
            raise HttpException(400,f"Jurusan dengan id {siswa.id_jurusan} tidak ditemukan")
    if siswa.id_kelas :
        findKelas = (await session.execute(select(Kelas).where(Kelas.id == siswa.id_kelas))).scalar_one_or_none()
        if not findKelas :
            raise HttpException(400,f"Kelas dengan id {siswa.id_kelas} tidak ditemukan")
    
    if siswa.model_dump(exclude_unset=True) :
        updateTable(siswa.model_dump(exclude={"alamat"}),findSiswa)

    if siswa.alamat :
        updateTable(siswa.alamat, findSiswa)
    
    siswaDictCopy = deepcopy(findSiswa.__dict__)
    
    await session.commit()
    return {
        "msg" : "success",
        "data" : siswaDictCopy
    }

PROFILE_STORE = os.getenv("DEV_FOTO_PROFILE_SISWA_STORE")
PROFILE_BASE_URL = os.getenv("DEV_FOTO_PROFILE_SISWA_BASE_URL")

async def updateFotoProfile(id_siswa : int,foto_profile : UploadFile,session : AsyncSession) -> SiswaBase :
    findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id_siswa))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(404,f"siswa tidak ditemukan")

    ext_file = foto_profile.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{foto_profile.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{PROFILE_STORE}{file_name}"
        
    fotoProfileBefore = findSiswa.foto_profile

    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(foto_profile.file.read())
        print(PROFILE_BASE_URL)
        findSiswa.foto_profile = f"{PROFILE_BASE_URL}/{file_name}"
    
    if fotoProfileBefore :
        print(fotoProfileBefore)
        file_nama_db_split = fotoProfileBefore.split("/")
        file_name_db = file_nama_db_split[-1]
        os.remove(f"{PROFILE_STORE}/{file_name_db}")
    
    siswaDictCopy = deepcopy(findSiswa.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : siswaDictCopy
    }

async def sendOtpForVerifySiswa(id_siswa : int,session : AsyncSession) -> SiswaBase :
    findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id_siswa))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(404,f"siswa tidak ditemukan")
    
    otp = await sendOtp(findSiswa.email)
    findSiswa.OTP_code = otp
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : findSiswa
    }
