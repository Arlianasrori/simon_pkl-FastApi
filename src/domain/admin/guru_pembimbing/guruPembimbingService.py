from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload

# models
from .guruPembimbingModel import AddGuruPembimbingBody, UpdateGuruPembimbingBody,ResponseGuruPembimbingPag
from ...models_domain.guru_pembimbing_model import GuruPembimbingBase,GuruPembimbingWithAlamat
from ...models_domain.alamat_model import AlamatBase,UpdateAlamatBody
from ....models.guruPembimbingModel import GuruPembimbing,AlamatGuruPembimbing
from ....models.sekolahModel import TahunSekolah

# common
import math
import os
from copy import deepcopy
from python_random_strings import random_strings
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable

async def addGuruPembimbing(id_sekolah : int,guruPembimbing : AddGuruPembimbingBody,alamat : AlamatBase,session : AsyncSession) -> GuruPembimbingWithAlamat:
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.nip == guruPembimbing.nip))).scalar_one_or_none()
    if findGuruPembimbing :
        raise HttpException(400,f"Guru Pembimbing dengan nip {guruPembimbing.nip} telah ditambahkan")
    
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.no_telepon == guruPembimbing.no_telepon))).scalar_one_or_none()
    if findGuruPembimbing :
        raise HttpException(400,f"nomor telepon {guruPembimbing.no_telepon} sudah ditambahkan")
    
    findTahun = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == guruPembimbing.id_tahun))).scalar_one_or_none()
    if not findTahun :
        raise HttpException(400,f"Tahun dengan id {guruPembimbing.id_tahun} tidak ditemukan")
    
    guruPembimbingMapping = guruPembimbing.model_dump()
    guruPembimbingMapping.update({"id" : random_strings.random_digits(6),"id_sekolah" : id_sekolah})
    alamatMapping = alamat.model_dump()
    alamatMapping.update({"id_guru_pembimbing" : guruPembimbingMapping["id"]})
    session.add(GuruPembimbing(**guruPembimbingMapping,alamat = AlamatGuruPembimbing(**alamatMapping)))
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : {
            **guruPembimbingMapping,
            "foto_profile" : None,
            "token_FCM" : None,
            "alamat" : alamatMapping
        }
    }

PROFILE_STORE = os.getenv("DEV_FOTO_PROFILE_GURU_PEMBIMBING_STORE")
PROFILE_BASE_URL = os.getenv("DEV_FOTO_PROFILE_GURU_PEMBIMBING_BASE_URL")

async def add_update_foto_profile(id : int,id_sekolah : int,foto_profile : UploadFile,session : AsyncSession) -> GuruPembimbingBase :
    findguruPembimbing = (await session.execute(select(GuruPembimbing).where(and_(GuruPembimbing.id == id,GuruPembimbing.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findguruPembimbing :
        raise HttpException(404,f"guru pembimbing tidak ditemukan")

    ext_file = foto_profile.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{random_strings.random_digits(12)}-{foto_profile.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{PROFILE_STORE}{file_name}"
        
    fotoProfileBefore = findguruPembimbing.foto_profile

    with open(file_name_save, "wb") as f:
        f.write(foto_profile.file.read())
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

async def getAllGuruPembimbing(page : int | None,id_sekolah : int,id_tahun : int,session : AsyncSession) -> GuruPembimbingWithAlamat | ResponseGuruPembimbingPag:
    statementGetGuru = select(GuruPembimbing).options(joinedload(GuruPembimbing.alamat)).where(and_(GuruPembimbing.id_sekolah == id_sekolah,GuruPembimbing.id_tahun == id_tahun))

    if page :
        guruPembimbing = (await session.execute(statementGetGuru.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(GuruPembimbing.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : guruPembimbing,
                "count_data" : len(guruPembimbing),
                "count_page" : countPage
            }
        }
    else :
        guruPembimbing = (await session.execute(statementGetGuru)).scalars().all()
        return {
            "msg" : "success",
            "data" : guruPembimbing
        }

async def getGuruPembimbingById(id : int,id_sekolah : int,session : AsyncSession) -> GuruPembimbingWithAlamat:
    guruPembimbing = (await session.execute(select(GuruPembimbing).options(joinedload(GuruPembimbing.alamat)).where(and_(GuruPembimbing.id == id,GuruPembimbing.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if not guruPembimbing :
        raise HttpException(404,f"Guru Pembimbing dengan id {id} tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : guruPembimbing
    }

async def updateGuruPembimbing(id : int,id_sekolah : int,guruPembimbing : UpdateGuruPembimbingBody,alamat : UpdateAlamatBody,session : AsyncSession) -> GuruPembimbingWithAlamat:
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).options(joinedload(GuruPembimbing.alamat)).where(and_(GuruPembimbing.id == id,GuruPembimbing.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findGuruPembimbing :
        raise HttpException(404,f"Guru Pembimbing dengan id {id} tidak ditemukan")
    
    if guruPembimbing.nip :
        findGuruPembimbingByNip = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.nip == guruPembimbing.nip))).scalar_one_or_none()
        if findGuruPembimbingByNip :
            raise HttpException(400,f"Guru Pembimbing dengan nip {guruPembimbing.nip} sudah ditambahkan")
    
    if guruPembimbing.no_telepon :
        findGuruPembimbingByNoTelepon = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.no_telepon == guruPembimbing.no_telepon))).scalar_one_or_none()
        if findGuruPembimbingByNoTelepon :
            raise HttpException(400,f"Guru Pembimbing dengan nomor telepon {guruPembimbing.no_telepon} sudah ditambahkan")
    
    if guruPembimbing.model_dump(exclude_unset=True) :
        updateTable(guruPembimbing,findGuruPembimbing)

    if alamat.model_dump(exclude_unset=True):
        updateTable(alamat,findGuruPembimbing.alamat)

    guruPembimbingDictCopy = deepcopy(findGuruPembimbing.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : guruPembimbingDictCopy
    }

async def deleteGuruPembimbing(id : int,id_sekolah : int,session : AsyncSession) -> GuruPembimbingBase:
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(and_(GuruPembimbing.id == id,GuruPembimbing.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findGuruPembimbing :
        raise HttpException(404,f"Guru Pembimbing dengan id {id} tidak ditemukan")
    
    await session.delete(findGuruPembimbing)
    guruPembimbingDictCopy = deepcopy(findGuruPembimbing.__dict__)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : guruPembimbingDictCopy
    }

