from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from .kunjunganModel import AddKunjunganBody,UpdateKunjunganBody,ResponseKunjunganDudiPag
from ...models_domain.kunjungan_guru_pembimbing_model import KunjunganGuruPembimbingWithDudi
from ....models.guruPembimbingModel import KunjunganGuruPembimbingPKL
from ....models.dudiModel import Dudi

# common
from copy import deepcopy
from ....error.errorHandling import HttpException
import math
from python_random_strings import random_strings
from ....utils.updateTable import updateTable

async def addKunjungan(id_guru : int,kunjungan : AddKunjunganBody,session : AsyncSession) -> KunjunganGuruPembimbingWithDudi :
    getDudi = (await session.execute(select(Dudi).where(Dudi.id == kunjungan.id_dudi))).scalar_one_or_none()
    if getDudi is None :
        raise HttpException(404,"dudi tidak ditemukan")
    
    
    kunjunganMapping = kunjungan.model_dump()
    kunjunganMapping.update({"id" : random_strings.random_digits(6),"id_guru_pembimbing" : id_guru})
    
    # nanti lanjut lagi add ke dataabase
    dudiDictCopy = deepcopy(getDudi.__dict__)
    session.add(KunjunganGuruPembimbingPKL(**kunjunganMapping))
    await session.commit()
    return{
        "msg" : "success",
        "data" : {
            **kunjunganMapping,
            "dudi" : dudiDictCopy
        }
    }

async def updateKunjungan(id_kunjungan : int,id_guru : int,kunjungan : UpdateKunjunganBody,session : AsyncSession) -> KunjunganGuruPembimbingWithDudi :
    getKunjungan = (await session.execute(select(KunjunganGuruPembimbingPKL).options(joinedload(KunjunganGuruPembimbingPKL.dudi)).where(and_(KunjunganGuruPembimbingPKL.id == id_kunjungan,KunjunganGuruPembimbingPKL.id_guru_pembimbing == id_guru)))).scalar_one_or_none()

    if getKunjungan is None :
        raise HttpException(404,"kunjungan tidak ditemukan")
    
    kunjunganDictCopy = getKunjungan.__dict__

    if kunjungan.model_dump() != {} :
        if kunjungan.id_dudi :
            getDudi = (await session.execute(select(Dudi).where(Dudi.id == kunjungan.id_dudi))).scalar_one_or_none()
            if getDudi is None :
                raise HttpException(404,"dudi tidak ditemukan")
           
        updateTable(kunjungan,getKunjungan)
        kunjunganDictCopy = deepcopy(getKunjungan.__dict__)
        await session.commit()
    
    return {
        "msg" : "success",
        "data" : kunjunganDictCopy
    }
        
async def getAllKunjungan(id_guru : int,page : int | None,session : AsyncSession) -> list[KunjunganGuruPembimbingWithDudi] | ResponseKunjunganDudiPag :
    statementSelectKunjungan = select(KunjunganGuruPembimbingPKL).options(joinedload(KunjunganGuruPembimbingPKL.dudi)).where(KunjunganGuruPembimbingPKL.id_guru_pembimbing == id_guru)
    
    if page :
        findKunjungan = (await session.execute(statementSelectKunjungan.limit(10).offset(10 * (page - 1)))).scalars().all()
        countData = (await session.execute(func.count(KunjunganGuruPembimbingPKL.id))).scalar_one()
        countPage = math.ceil(countData / 10)

        return {
            "msg" : "success",
            "data" : {
                "data" : findKunjungan,
                "count_data" : len(findKunjungan),
                "count_page" : countPage
            }
        }
    else :
        findKunjungan = (await session.execute(statementSelectKunjungan)).scalars().all()
        return {
            "msg" : "success",
            "data" : findKunjungan
        }
        
async def getKunjunganById(id_guru : int,id_kunjungan : int,session : AsyncSession) -> KunjunganGuruPembimbingWithDudi :
    getKunjungan = (await session.execute(select(KunjunganGuruPembimbingPKL).options(joinedload(KunjunganGuruPembimbingPKL.dudi)).where(and_(KunjunganGuruPembimbingPKL.id == id_kunjungan,KunjunganGuruPembimbingPKL.id_guru_pembimbing == id_guru)))).scalar_one_or_none()

    if getKunjungan is None :
        raise HttpException(404,"kunjungan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : getKunjungan
    }

async def deleteKunjungan(id_guru : int,id_kunjungan : int,session : AsyncSession) -> KunjunganGuruPembimbingWithDudi :
    getKunjungan = (await session.execute(select(KunjunganGuruPembimbingPKL).options(joinedload(KunjunganGuruPembimbingPKL.dudi)).where(and_(KunjunganGuruPembimbingPKL.id == id_kunjungan,KunjunganGuruPembimbingPKL.id_guru_pembimbing == id_guru)))).scalar_one_or_none()

    if getKunjungan is None :
        raise HttpException(404,"kunjungan tidak ditemukan")
    
    kunjunganDictCopy = deepcopy(getKunjungan.__dict__)
    await session.delete(getKunjungan)
    await session.commit()
    return {
        "msg" : "success",
        "data" : kunjunganDictCopy
    }
    