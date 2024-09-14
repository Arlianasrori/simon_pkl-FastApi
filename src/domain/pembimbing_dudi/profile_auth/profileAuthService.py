import os
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload

# models]
from ...models_domain.pembimbing_dudi_model import PembimbingDudiBase,PembimbingDudiWithAlamatDudi
from ....models.pembimbingDudiModel import PembimbingDudi
from .profileAuthModel import UpdateProfileBody

# common
from copy import deepcopy
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable
from python_random_strings import random_strings

async def getPembimbingDudi(id_pembimbing_dudi : int,session : AsyncSession) -> PembimbingDudiBase :
    print(id_pembimbing_dudi)
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id == id_pembimbing_dudi))).scalar_one_or_none()

    if not findPembimbingDudi :
        raise HttpException(404,"pembimbing dudi tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPembimbingDudi
    }

async def getProfile(id_pembimbing_dudi : int,session : AsyncSession) -> PembimbingDudiWithAlamatDudi :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).options(joinedload(PembimbingDudi.alamat),joinedload(PembimbingDudi.dudi)).where(PembimbingDudi.id == id_pembimbing_dudi))).scalar_one_or_none()

    if not findPembimbingDudi :
        raise HttpException(404,"pembimbing dudi tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPembimbingDudi
    }

async def updateProfile(id_pembimbing_dudi : int,pembimbingDudi : UpdateProfileBody,session : AsyncSession) -> PembimbingDudiBase :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id == id_pembimbing_dudi))).scalar_one_or_none()

    if not findPembimbingDudi :
        raise HttpException(404,f"Pembimbing Dudi dengan id {id_pembimbing_dudi} tidak ditemukan")

    if pembimbingDudi.username :
        findPembimbingDudiByUsername = (await session.execute(select(PembimbingDudi).where(and_(PembimbingDudi.username == pembimbingDudi.username,PembimbingDudi.id != id_pembimbing_dudi)))).scalar_one_or_none()
        if findPembimbingDudiByUsername :
            raise HttpException(400,f"Pembimbing Dudi dengan username {pembimbingDudi.username} sudah ada")
    print(pembimbingDudi.model_dump())
    if pembimbingDudi.model_dump() != {} :
        updateTable(pembimbingDudi,findPembimbingDudi)
    
    pembimbingDudiDictCopy = deepcopy(findPembimbingDudi.__dict__)
    await session.commit()
    return {
        "msg" : "success",
        "data" : pembimbingDudiDictCopy
    }

PROFILE_STORE = os.getenv("DEV_FOTO_PROFILE_PEMBIMBING_DUDI_STORE")
PROFILE_BASE_URL = os.getenv("DEV_FOTO_PROFILE_PEMBIMBING_DUDI_BASE_URL")

async def updateFotoProfile(id_pembimbing_dudi : int,foto_profile : UploadFile,session : AsyncSession) -> PembimbingDudiBase :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id == id_pembimbing_dudi))).scalar_one_or_none()
    if not findPembimbingDudi :
        raise HttpException(404,f"guru pembimbing tidak ditemukan")

    ext_file = foto_profile.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{foto_profile.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{PROFILE_STORE}{file_name}"
        
    fotoProfileBefore = findPembimbingDudi.foto_profile

    with open(file_name_save, "wb") as f:
        f.write(foto_profile.file.read())
        print(PROFILE_BASE_URL)
        findPembimbingDudi.foto_profile = f"{PROFILE_BASE_URL}/{file_name}"
    
    if fotoProfileBefore :
        print(fotoProfileBefore)
        file_nama_db_split = fotoProfileBefore.split("/")
        file_name_db = file_nama_db_split[-1]
        os.remove(f"{PROFILE_STORE}/{file_name_db}")
    
    pembimbingDudiDictCopy = deepcopy(findPembimbingDudi.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : pembimbingDudiDictCopy
    }