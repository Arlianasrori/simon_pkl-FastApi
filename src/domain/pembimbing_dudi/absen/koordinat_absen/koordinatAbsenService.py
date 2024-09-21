from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_
from sqlalchemy.orm import joinedload

# models
from .koordinatAbsenModel import AddkoordinatAbsenBody,UpdatekoordinaatAbsenBody
from ....models_domain.absen_model import koordinatAbsenBase
from .....models.absenModel import KoordinatAbsen

# common
from python_random_strings import random_strings
from copy import deepcopy
from .....error.errorHandling import HttpException
from .koordinatAbsenUtils import is_valid_coordinate,is_valid_latitude,is_valid_longitude

async def addkoordinatAbsen(id_dudi : int,koordinat : AddkoordinatAbsenBody,session : AsyncSession) -> koordinatAbsenBase :
    isValidKoordinat = await is_valid_coordinate(koordinat.latitude,koordinat.longitude)

    if not isValidKoordinat :
        raise HttpException(400,"koordinat tidak valid")
    
    koordinatMapping = koordinat.model_dump()
    koordinatMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi})

    session.add(KoordinatAbsen(**koordinatMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : koordinatMapping
    }

async def getAllkoordinatAbsen(id_dudi : int,session : AsyncSession) -> list[koordinatAbsenBase] :
    findKoordinat = (await session.execute(select(KoordinatAbsen).where(KoordinatAbsen.id_dudi == id_dudi))).scalars().all()

    return {
        "msg" : "success",
        "data" : findKoordinat
    }

async def getKoordinatById(id_dudi : int,id_koordinat : str,session : AsyncSession) -> koordinatAbsenBase :
    findKoordinat = (await session.execute(select(KoordinatAbsen).where(and_(KoordinatAbsen.id_dudi == id_dudi,KoordinatAbsen.id == id_koordinat)))).scalar_one_or_none()

    if not findKoordinat :
        raise HttpException(404,"koordinat tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findKoordinat
    }

async def updatekoordinatAbsen(id_dudi : int,id_koordinat : str,koordinat : UpdatekoordinaatAbsenBody,session : AsyncSession) -> koordinatAbsenBase :
    findKoordinat = (await session.execute(select(KoordinatAbsen).where(and_(KoordinatAbsen.id_dudi == id_dudi,KoordinatAbsen.id == id_koordinat)))).scalar_one_or_none()

    if not findKoordinat :
        raise HttpException(404,"koordinat tidak ditemukan")
    
    if koordinat.latitude :
        if not is_valid_latitude(koordinat.latitude) :
            raise HttpException(400,"koordinat latitude tidak valid")
        findKoordinat.latitude = koordinat.latitude
    if koordinat.longitude :
        if not is_valid_longitude(koordinat.longitude) :
            raise HttpException(400,"koordinat longitude tidak valid")
        findKoordinat.longitude = koordinat.longitude
    koordinatDictCopy = deepcopy(findKoordinat.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : koordinatDictCopy
    }

async def deleteKoordinat(id_dudi : int,id_koordinat : str,session : AsyncSession) -> koordinatAbsenBase :
    findKoordinat = (await session.execute(select(KoordinatAbsen).where(and_(KoordinatAbsen.id_dudi == id_dudi,KoordinatAbsen.id == id_koordinat)))).scalar_one_or_none()

    if not findKoordinat :
        raise HttpException(404,"koordinat tidak ditemukan")
    
    koordinatDictCopy = deepcopy(findKoordinat.__dict__)
    await session.delete(findKoordinat)
    await session.commit()

    return {
        "msg" : "success",
        "data" : koordinatDictCopy
    }