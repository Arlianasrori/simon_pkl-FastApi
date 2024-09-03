from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload

# models
from .pembimbingDudiModel import AddPembimbingDudiBody,UpdatePembimbingDudiBody,ResponsePembimbingDudiPagination
from ....models.dudiModel import Dudi
from ...models_domain.pembimbing_dudi_model import PembimbingDudiBase, PembimbingDudiWithAlamatDudi
from ....models.pembimbingDudiModel import PembimbingDudi,AlamatPembimbingDudi
from ...models_domain.alamat_model import AlamatBase,UpdateAlamatBody
from ....models.sekolahModel import TahunSekolah

# common
from copy import deepcopy
import math
import os
from python_random_strings import random_strings
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable

async def addPembimbingDudi(id_sekolah : int,pembimbingDudi : AddPembimbingDudiBody,alamat : AlamatBase,session : AsyncSession) -> PembimbingDudiWithAlamatDudi :
    findTahun = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == pembimbingDudi.id_tahun))).scalar_one_or_none()
    if not findTahun :
        raise HttpException(404,f"Tahun Sekolah dengan id {pembimbingDudi.id_tahun} tidak ditemukan")
    
    findDudi = (await session.execute(select(Dudi).where(Dudi.id == pembimbingDudi.id_dudi))).scalar_one_or_none()
    if not findDudi :
        raise HttpException(404,f"Dudi dengan id {pembimbingDudi.id_dudi} tidak ditemukan")
    
    pembimbingDudiMapping = pembimbingDudi.model_dump()
    pembimbingDudiMapping.update({"id" : random_strings.random_digits(6),"id_sekolah" : id_sekolah})
    alamatPembimbingDudiMapping = alamat.model_dump()
    alamatPembimbingDudiMapping.update({"id_pembimbing_dudi" : pembimbingDudiMapping["id"]})
    
    dudiDictCopy = deepcopy(findDudi.__dict__)
    session.add(PembimbingDudi(**pembimbingDudiMapping,alamat = AlamatPembimbingDudi(**alamatPembimbingDudiMapping)))
    print("tes")
    await session.commit()

    return {
        "msg" : "success",
        "data" : {
            **pembimbingDudiMapping,
            "foto_profile" : None,
            "token_FCM" : None,
            "alamat" : alamatPembimbingDudiMapping,
            "dudi" : dudiDictCopy
        }
    }

PROFILE_STORE = os.getenv("DEV_FOTO_PROFILE_PEMBIMBING_DUDI_STORE")
PROFILE_BASE_URL = os.getenv("DEV_FOTO_PROFILE_PEMBIMBING_DUDI_BASE_URL")

async def add_update_foto_profile(id : int,id_sekolah : int,foto_profile : UploadFile,session : AsyncSession) -> PembimbingDudiBase :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(and_(PembimbingDudi.id == id,PembimbingDudi.id_sekolah == id_sekolah)))).scalar_one_or_none()
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

async def getAllPembimbingDudi(page : int,id_sekolah : int,id_tahun : int,session : AsyncSession) -> list[PembimbingDudiWithAlamatDudi] | ResponsePembimbingDudiPagination:
    getPembimbingDudiStatement = select(PembimbingDudi).where(and_(PembimbingDudi.id_sekolah == id_sekolah,PembimbingDudi.id_tahun == id_tahun)).options(joinedload(PembimbingDudi.alamat),joinedload(PembimbingDudi.dudi))

    if page : 
        findPembimbingDudi = (await session.execute(getPembimbingDudiStatement.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(PembimbingDudi.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findPembimbingDudi,
                "count_data" : len(findPembimbingDudi),
                "count_page" : countPage
            }
        }
    else :
        findPembimbingDudi = (await session.execute(getPembimbingDudiStatement)).scalars().all()
        print(findPembimbingDudi)
        return {
            "msg" : "success",
            "data" : findPembimbingDudi
        }

async def getPembimbingDudiById(id_sekolah : int,id_pembimbing_dudi : int,session : AsyncSession) -> PembimbingDudiWithAlamatDudi :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(and_(PembimbingDudi.id == id_pembimbing_dudi,PembimbingDudi.id_sekolah == id_sekolah)).options(joinedload(PembimbingDudi.alamat),joinedload(PembimbingDudi.dudi)))).scalar_one_or_none()
    if not findPembimbingDudi :
        raise HttpException(404,f"Pembimbing Dudi dengan id {id_pembimbing_dudi} tidak ditemukan")
    return {
        "msg" : "success",
        "data" : findPembimbingDudi
    }

async def updatePembimbingDudi(id_sekolah : int,id_pembimbing_dudi : int,pembimbingDudi : UpdatePembimbingDudiBody,alamat : UpdateAlamatBody,session : AsyncSession) -> PembimbingDudiWithAlamatDudi :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).options(joinedload(PembimbingDudi.alamat),joinedload(PembimbingDudi.dudi)).where(and_(PembimbingDudi.id == id_pembimbing_dudi,PembimbingDudi.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if not findPembimbingDudi :
        raise HttpException(404,f"Pembimbing Dudi dengan id {id_pembimbing_dudi} tidak ditemukan")

    if pembimbingDudi.id_dudi :
        findDudi = (await session.execute(select(Dudi).where(Dudi.id == pembimbingDudi.id_dudi))).scalar_one_or_none()
        if not findDudi :
            raise HttpException(404,f"Dudi dengan id {pembimbingDudi.id_dudi} tidak ditemukan")

    if pembimbingDudi.model_dump() != {} :
        updateTable(pembimbingDudi,findPembimbingDudi)
    if alamat.model_dump() != {} :
        updateTable(alamat,findPembimbingDudi.alamat)
    
    pembimbingDudiDictCopy = deepcopy(findPembimbingDudi.__dict__)
    await session.commit()
    return {
        "msg" : "success",
        "data" : pembimbingDudiDictCopy
    }
    
async def deletePembimbingDudi(id_sekolah : int,id_pembimbing_dudi : int,session : AsyncSession) -> PembimbingDudiBase :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(and_(PembimbingDudi.id == id_pembimbing_dudi,PembimbingDudi.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findPembimbingDudi :
        raise HttpException(404,f"Pembimbing Dudi dengan id {id_pembimbing_dudi} tidak ditemukan")
    
    pembimbingDudiDictCopy = deepcopy(findPembimbingDudi.__dict__)
    await session.delete(findPembimbingDudi)
    await session.commit()
    return {
        "msg" : "success",
        "data" : pembimbingDudiDictCopy
    }