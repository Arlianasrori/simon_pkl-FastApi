from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from sqlalchemy.orm import joinedload,subqueryload

# models
from .jurusanKelasModel import AddJurusanBody, AddKelasBody,UpdateJurusanBody,UpdateKelasBody
from ....models.siswaModel import Jurusan, Kelas
from ....models.sekolahModel import TahunSekolah
from ...models_domain.kelas_jurusan_model import JurusanBase,MoreJurusanBase,KelasBase,KelasWithJurusan

# common
from copy import deepcopy
from python_random_strings import random_strings
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable

# jurusan
async def addJurusan(id_sekolah : int,jurusan : AddJurusanBody, session : AsyncSession) -> JurusanBase :
    findTahunById = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == jurusan.id_tahun))).scalar_one_or_none()

    if not findTahunById :
        raise HttpException(404,f"tahun sekolah dengan id {jurusan.id_tahun} tidak ditemukan")


    findJurusanByName = (await session.execute(select(Jurusan).where(and_(Jurusan.nama == jurusan.nama,Jurusan.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if findJurusanByName :
        raise HttpException(400,f"jurusan dengan nama {jurusan.nama} telah ditambahkan")
    
    jurusanMapping = jurusan.model_dump()
    jurusanMapping.update({"id" : random_strings.random_digits(6),"id_sekolah" : id_sekolah})

    session.add(Jurusan(**jurusanMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : jurusanMapping
    }

async def getAllJurusan(id_sekolah : int,id_tahun : int,session : AsyncSession) -> list[JurusanBase] :
    findAllJurusan = (await session.execute(select(Jurusan).where(and_(Jurusan.id_sekolah == id_sekolah,Jurusan.id_tahun == id_tahun)))).scalars().all()
    return {
        "msg" : "success",
        "data" : findAllJurusan
    }

async def getJurusanById(id : int, session : AsyncSession) -> MoreJurusanBase :
    findJurusanById = (await session.execute(select(Jurusan).options(subqueryload(Jurusan.kelas)).where(Jurusan.id == id))).scalar_one_or_none()

    if not findJurusanById :
        raise HttpException(404,f"jurusan dengan id {id} tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findJurusanById
    }

async def updateJurusan(id : int,jurusan : UpdateJurusanBody,id_sekolah : int, session : AsyncSession) -> JurusanBase :
    findJurusanById = (await session.execute(select(Jurusan).where(and_(Jurusan.id == id,Jurusan.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if not findJurusanById :
        raise HttpException(404,f"jurusan dengan id {id} tidak ditemukan")
    
    jurusanDictCopy = findJurusanById.__dict__
    if jurusan.nama :
        findJurusanByName = (await session.execute(select(Jurusan).where(and_(Jurusan.nama == jurusan.nama,Jurusan.id_sekolah == findJurusanById.id_sekolah)))).scalar_one_or_none()

        if findJurusanByName :
            raise HttpException(400,f"jurusan dengan nama {jurusan.nama} telah ditambahkan")

        findJurusanById.nama = jurusan.nama
        jurusanDictCopy = deepcopy(findJurusanById.__dict__)
        await session.commit()  

    return {
        "msg" : "success",
        "data" : jurusanDictCopy
    } 

async def deleteJurusan(id : int,id_sekolah : int, session : AsyncSession) -> JurusanBase :
    findJurusanById = (await session.execute(select(Jurusan).where(and_(Jurusan.id == id,Jurusan.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if not findJurusanById :
        raise HttpException(404,f"jurusan dengan id {id} tidak ditemukan")
    
    jurusanDictCopy = deepcopy(findJurusanById.__dict__)
    await session.delete(findJurusanById)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : jurusanDictCopy
    }

#  kelas
async def addKelas(id_sekolah : int,kelas : AddKelasBody, session : AsyncSession) -> KelasBase :
    findJurusanById = (await session.execute(select(Jurusan).where(and_(Jurusan.id == kelas.id_jurusan,Jurusan.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if not findJurusanById :
        raise HttpException(404,f"jurusan dengan id {kelas.id_jurusan} tidak ditemukan")
    
    kelasMapping = kelas.model_dump()
    kelasMapping.update({"id" : random_strings.random_digits(6)})
    session.add(Kelas(**kelasMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : kelasMapping
    }
    
async def getAllKelas(id_sekolah : int,id_tahun : int,session : AsyncSession) -> list[KelasBase] :
    findAllKelas = (await session.execute(select(Kelas).where(and_(Kelas.jurusan.has(Jurusan.id_sekolah == id_sekolah),Kelas.jurusan.has(Jurusan.id_tahun == id_tahun))))).scalars().all()
    return {
        "msg" : "success",
        "data" : findAllKelas
    }

async def getKelasById(id : int, session : AsyncSession) -> KelasWithJurusan :
    findKelasById = (await session.execute(select(Kelas).options(joinedload(Kelas.jurusan)).where(Kelas.id == id))).scalar_one_or_none()

    if not findKelasById :
        raise HttpException(404,f"kelas dengan id {id} tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findKelasById
    }

async def updateKelas(id : int,id_sekolah : int,kelas : UpdateKelasBody, session : AsyncSession) -> KelasBase :
    findKelasById = (await session.execute(select(Kelas).where(and_(Kelas.id == id,Kelas.jurusan.has(Jurusan.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findKelasById :
        raise HttpException(404,f"kelas dengan id {id} tidak ditemukan")
    
    if kelas.id_jurusan :
        findJurusanById = (await session.execute(select(Jurusan).where(and_(Jurusan.id == kelas.id_jurusan,Jurusan.id_sekolah == id_sekolah)))).scalar_one_or_none()

        if not findJurusanById :
            raise HttpException(404,f"jurusan dengan id {kelas.id_jurusan} tidak ditemukan")

    kelasDictCopy = findKelasById.__dict__

    if kelas :
        updateTable(kelas,findKelasById)
        kelasDictCopy = deepcopy(findKelasById.__dict__)
        await session.commit()

    return {
        "msg" : "success",
        "data" : kelasDictCopy
    }

async def deleteKelas(id : int,id_sekolah : int, session : AsyncSession) -> KelasBase :
    findKelasById = (await session.execute(select(Kelas).where(and_(Kelas.id == id,Kelas.jurusan.has(Jurusan.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findKelasById :
        raise HttpException(404,f"kelas dengan id {id} tidak ditemukan")
    
    kelasDictCopy = deepcopy(findKelasById.__dict__)
    await session.delete(findKelasById)
    await session.commit()

    return {
        "msg" : "success",
        "data" : kelasDictCopy
    }

