from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload

# models
from .dudiModel import AddDudiBody,UpdateDudiBody,ResponseDudiPag
from ...models_domain.dudi_model import DudiBase, DudiWithAlamat, DudiWithAlamatKuota
from ...models_domain.alamat_model import AlamatBase,UpdateAlamatBody
from ....models.dudiModel import Dudi,AlamatDudi
from ....models.sekolahModel import TahunSekolah

# common
from copy import deepcopy
import math
import os
from python_random_strings import random_strings
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable

async def addDudi(id_sekolah : int,dudi : AddDudiBody,alamat : AlamatBase,session : AsyncSession) -> DudiWithAlamat :
    """
    Add a new DUDI (Dunia Usaha dan Dunia Industri) entry.

    Args:
        id_sekolah (int): The school ID.
        dudi (AddDudiBody): The DUDI data to be added.
        alamat (AlamatBase): The address data for the DUDI.
        session (AsyncSession): The database session.

    Returns:
        DudiWithAlamat: The newly added DUDI with its address.

    Raises:
        HttpException: If the specified school year is not found.
    """
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
    """
    Retrieve all DUDI entries for a specific school and year.

    Args:
        page (int): The page number for pagination.
        id_sekolah (int): The school ID.
        id_tahun (int): The year ID.
        session (AsyncSession): The database session.

    Returns:
        list[DudiWithAlamat] | ResponseDudiPag: A list of DUDI entries or paginated response.
    """
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

async def getDudiById(id_dudi : int,id_sekolah : int,session : AsyncSession) -> DudiWithAlamatKuota :
    """
    Retrieve a specific DUDI entry by its ID.

    Args:
        id_dudi (int): The DUDI ID.
        id_sekolah (int): The school ID.
        session (AsyncSession): The database session.

    Returns:
        DudiWithAlamatKuota: The DUDI entry with its address and quota.

    Raises:
        HttpException: If the DUDI entry is not found.
    """
    findDudi = (await session.execute(select(Dudi).where(and_(Dudi.id == id_dudi,Dudi.id_sekolah == id_sekolah)).options(joinedload(Dudi.alamat),joinedload(Dudi.kuota)))).scalar_one_or_none()
    if not findDudi :
        raise HttpException(404,f"Dudi dengan id {id_dudi} tidak ditemukan")
    
    print(findDudi.__dict__)
    return {
        "msg" : "success",
        "data" : findDudi
    }

async def updateDudi(id_dudi : int,id_sekolah : int,dudi : UpdateDudiBody,alamat : UpdateAlamatBody,session : AsyncSession) -> DudiWithAlamat :
    """
    Update a DUDI entry and its address.

    Args:
        id_dudi (int): The DUDI ID.
        id_sekolah (int): The school ID.
        dudi (UpdateDudiBody): The updated DUDI data.
        alamat (UpdateAlamatBody): The updated address data.
        session (AsyncSession): The database session.

    Returns:
        DudiWithAlamat: The updated DUDI entry with its address.

    Raises:
        HttpException: If the DUDI entry is not found.
    """
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
    """
    Delete a DUDI entry.

    Args:
        id_dudi (int): The DUDI ID.
        id_sekolah (int): The school ID.
        session (AsyncSession): The database session.

    Returns:
        DudiBase: The deleted DUDI entry.

    Raises:
        HttpException: If the DUDI entry is not found.
    """
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