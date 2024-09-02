from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload

# models
from .tahunSekolahModel import AddTahunSekolahBody,UpdateTahunSekolahBody
from ...models_domain.sekolah_model import TahunSekolahBase
from ....models.sekolahModel import TahunSekolah

# common
from copy import deepcopy
from python_random_strings import random_strings
from ....error.errorHandling import HttpException

async def addTahunSekolah(id_sekolah : int,tahun : AddTahunSekolahBody,session : AsyncSession) -> TahunSekolahBase :
    findTahunById = (await session.execute(select(TahunSekolah).where(and_(TahunSekolah.id_sekolah == id_sekolah,TahunSekolah.tahun == tahun.tahun)))).scalar_one_or_none()

    if findTahunById :
        raise HttpException(400,f"tahun {tahun.tahun} sudah ada")
    
    tahunMapping = tahun.model_dump()
    tahunMapping.update({"id" : random_strings.random_digits(6),"id_sekolah" : id_sekolah})
    
    session.add(TahunSekolah(**tahunMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : {
            **tahunMapping,
            "id_sekolah" : id_sekolah
        }
    }

async def getAllTahunSekolah(id_sekolah : int,session : AsyncSession) -> list[TahunSekolahBase] :
    findTahunById = (await session.execute(select(TahunSekolah).where(TahunSekolah.id_sekolah == id_sekolah))).scalars().all()

    return {
        "msg" : "success",
        "data" : findTahunById
    }

async def updateTahunSekolah(id_sekolah : int,id_tahun : int,tahun : UpdateTahunSekolahBody,session : AsyncSession) -> TahunSekolahBase :
    findTahunById = (await session.execute(select(TahunSekolah).where(and_(TahunSekolah.id_sekolah == id_sekolah,TahunSekolah.id == id_tahun)))).scalar_one_or_none()

    if not findTahunById :
        raise HttpException(404,f"tahun dengan id {id_tahun} tidak ditemukan")
    
    tahunDictCopy = findTahunById.__dict__
    if tahun.tahun :
        findTahunByTahun = (await session.execute(select(TahunSekolah).where(and_(TahunSekolah.id_sekolah == id_sekolah,TahunSekolah.tahun == tahun.tahun)))).scalar_one_or_none()

        if findTahunByTahun :
            raise HttpException(400,f"tahun {tahun.tahun} telah ditambahkan")

        findTahunById.tahun = tahun.tahun
        tahunDictCopy = deepcopy(findTahunById.__dict__)
        await session.commit()

    return {
        "msg" : "success",
        "data" : tahunDictCopy
    }
    
async def deleteTahunSekolah(id_sekolah : int,id_tahun : int,session : AsyncSession) -> TahunSekolahBase :
    findTahunById = (await session.execute(select(TahunSekolah).where(and_(TahunSekolah.id_sekolah == id_sekolah,TahunSekolah.id == id_tahun)))).scalar_one_or_none()

    if not findTahunById :
        raise HttpException(404,f"tahun dengan id {id_tahun} tidak ditemukan")
    
    tahunDictCopy = deepcopy(findTahunById.__dict__)
    await session.delete(findTahunById)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : tahunDictCopy
    }