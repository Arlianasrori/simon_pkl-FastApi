from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload

# models
from .dudiModel import AddDudiBody,UpdateDudiBody,ResponseDudiPag
from ...models_domain.dudi_model import DudiBase, DudiWithAlamat, DudiWithAlamatKouta
from ...models_domain.alamat_model import AlamatBase,UpdateAlamatBody
from ....models.dudiModel import Dudi,AlamatDudi,KoutaSiswa
from ....models.sekolahModel import TahunSekolah

# common
from copy import deepcopy
import math
import os
from python_random_strings import random_strings
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable

async def addDudi(id_sekolah : int,dudi : AddDudiBody,alamat : AlamatBase,session : AsyncSession) -> DudiWithAlamat :
    findTahun = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == dudi.id_tahun))).scalar_one_or_none()
    if not findTahun :
        raise HttpException(404,f"Tahun Sekolah dengan id {dudi.id_tahun} tidak ditemukan")
    
    dudiMapping = dudi.model_dump()
    dudiMapping.update({"id" : random_strings.random_digits(6),"id_sekolah" : id_sekolah})
    alamatMapping = alamat.model_dump()
    alamatMapping.update({"id_dudi" : dudiMapping["id"]})
    session.add(Dudi(**dudiMapping,alamat = AlamatDudi(**alamatMapping)))
    await session.commit()
    return {
        "msg" : "success",
        "data" : {
            **dudiMapping,
            "tersedia" : False,
            "alamat" : alamatMapping
        }
    }

async def getAllDudi(page : int,id_sekolah : int,id_tahun : int,session : AsyncSession) -> list[DudiWithAlamat] | ResponseDudiPag:
    statementGetDudi = select(Dudi).where(and_(Dudi.id_sekolah == id_sekolah,Dudi.id_tahun == id_tahun)).options(joinedload(Dudi.alamat))

    if page :
        findDudi = (await session.execute(statementGetDudi.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(Dudi.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findDudi,
                "count_data" : len(findDudi),
                "count_page" : countPage
            }
        }
    else :
        findDudi = (await session.execute(statementGetDudi)).scalars().all()
        return {
        "msg" : "success",
        "data" : findDudi
    }

async def getDudiById(id_dudi : int,id_sekolah : int,session : AsyncSession) -> DudiWithAlamatKouta :
    findDudi = (await session.execute(select(Dudi).where(and_(Dudi.id == id_dudi,Dudi.id_sekolah == id_sekolah)).options(joinedload(Dudi.alamat),joinedload(Dudi.kouta)))).scalar_one_or_none()
    if not findDudi :
        raise HttpException(404,f"Dudi dengan id {id_dudi} tidak ditemukan")
    
    print(findDudi.__dict__)
    return {
        "msg" : "success",
        "data" : findDudi
    }

async def updateDudi(id_dudi : int,id_sekolah : int,dudi : UpdateDudiBody,alamat : UpdateAlamatBody,session : AsyncSession) -> DudiWithAlamat :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.alamat)).where(and_(Dudi.id == id_dudi,Dudi.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findDudi :
        raise HttpException(404,f"Dudi dengan id {id_dudi} tidak ditemukan")
    
    if dudi.model_dump() != {} :
        updateTable(dudi,findDudi)
    if alamat.model_dump() != {} :
        updateTable(alamat,findDudi.alamat)
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    return {
        "msg" : "success",
        "data" : dudiDictCopy
    }

async def deleteDudi(id_dudi : int,id_sekolah : int,session : AsyncSession) -> DudiBase :
    findDudi = (await session.execute(select(Dudi).where(and_(Dudi.id == id_dudi,Dudi.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findDudi :
        raise HttpException(404,f"Dudi dengan id {id_dudi} tidak ditemukan")
    await session.delete(findDudi)
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    return {
        "msg" : "success",
        "data" : dudiDictCopy
    }

