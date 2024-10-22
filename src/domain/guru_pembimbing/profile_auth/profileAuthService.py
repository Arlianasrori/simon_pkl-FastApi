from copy import deepcopy
import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload

# models
from ...models_domain.guru_pembimbing_model import GuruPembimbingBase,GuruPembimbingWithSekolahAlamat
from ....models.guruPembimbingModel import GuruPembimbing
from .profileAuthModel import UpdateProfileBody

# common 
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable
from python_random_strings import random_strings
import os
from ....utils.sendOtp import sendOtp

async def getGuruPembimbing(id_guru_pembimbing : int,session : AsyncSession) -> GuruPembimbingBase :
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == id_guru_pembimbing))).scalar_one_or_none()

    if not findGuruPembimbing :
        raise HttpException(404,"guru pembimbing tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findGuruPembimbing
    }

async def getProfileAuth(id_guru_pembimbing : int,session : AsyncSession) -> GuruPembimbingWithSekolahAlamat :
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).options(joinedload(GuruPembimbing.alamat),joinedload(GuruPembimbing.sekolah)).where(GuruPembimbing.id == id_guru_pembimbing))).scalar_one_or_none()

    if not findGuruPembimbing :
        raise HttpException(404,"guru pembimbing tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findGuruPembimbing
    }


async def updateProfile(id_guru : int,guruPembimbing : UpdateProfileBody,session : AsyncSession) -> GuruPembimbingBase:
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == id_guru))).scalar_one_or_none()
    if not findGuruPembimbing :
        raise HttpException(404,f"Guru Pembimbing dengan id {id_guru} tidak ditemukan")
    
    if guruPembimbing.nip :
        findGuruPembimbingByNip = (await session.execute(select(GuruPembimbing).where(and_(GuruPembimbing.nip == guruPembimbing.nip,GuruPembimbing.id != id_guru)))).scalar_one_or_none()
        if findGuruPembimbingByNip :
            raise HttpException(400,f"Guru Pembimbing dengan nip {guruPembimbing.nip} sudah ditambahkan")
    
    if guruPembimbing.no_telepon :
        findGuruPembimbingByNoTelepon = (await session.execute(select(GuruPembimbing).where(and_(GuruPembimbing.no_telepon == guruPembimbing.no_telepon,GuruPembimbing.id != id_guru)))).scalar_one_or_none()
        if findGuruPembimbingByNoTelepon :
            raise HttpException(400,f"Guru Pembimbing dengan nomor telepon {guruPembimbing.no_telepon} sudah ditambahkan")
    
    if guruPembimbing.model_dump(exclude_unset=True) :
        updateTable(guruPembimbing,findGuruPembimbing)

    guruPembimbingDictCopy = deepcopy(findGuruPembimbing.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : guruPembimbingDictCopy
    }


PROFILE_STORE = os.getenv("DEV_FOTO_PROFILE_GURU_PEMBIMBING_STORE")
PROFILE_BASE_URL = os.getenv("DEV_FOTO_PROFILE_GURU_PEMBIMBING_BASE_URL")
async def updateFotoProfile(id_guru : int,foto_profile : UploadFile,session : AsyncSession) -> GuruPembimbingBase :
    findguruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == id_guru))).scalar_one_or_none()
    if not findguruPembimbing :
        raise HttpException(404,f"guru pembimbing tidak ditemukan")

    ext_file = foto_profile.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{foto_profile.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{PROFILE_STORE}{file_name}"
        
    fotoProfileBefore = findguruPembimbing.foto_profile

    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(foto_profile.file.read())
        print(PROFILE_BASE_URL)
        findguruPembimbing.foto_profile = f"{PROFILE_BASE_URL}/{file_name}"
    
    if fotoProfileBefore :
        print(fotoProfileBefore)
        file_nama_db_split = fotoProfileBefore.split("/")
        file_name_db = file_nama_db_split[-1]
        os.remove(f"{PROFILE_STORE}/{file_name_db}")
    
    guruDictCopy = deepcopy(findguruPembimbing.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : guruDictCopy
    } 

async def sendOtpForVerifyGuru(id_guru : int,session : AsyncSession) -> GuruPembimbingBase :
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == id_guru))).scalar_one_or_none()
    if not findGuruPembimbing :
        raise HttpException(404,f"guru pembimbing tidak ditemukan")
    
    otp = await sendOtp(findGuruPembimbing.email)
    findGuruPembimbing.OTP_code = otp
    await session.commit()

    return {
        "msg" : "success",
        "data" : findGuruPembimbing
    }