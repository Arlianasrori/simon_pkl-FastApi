from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ...models_domain.pengajuan_cancel_pkl_model import PengajuanCancelPklWithDudi,PengajuanCancelPklBase
from ....models.pengajuanPklModel import PengajuanCancelPKL,StatusCancelPKLENUM
from ....models.siswaModel import Siswa,StatusPKLEnum
from ....models.pembimbingDudiModel import PembimbingDudi

# common
from ....error.errorHandling import HttpException
from python_random_strings import random_strings
from datetime import datetime

from multiprocessing import Process

# notification
from ..notification.notifUtils import runningProccessSync

async def addPengajuanCancelPkl(id_siswa : int,session : AsyncSession) -> PengajuanCancelPklBase :
    findSiswa = (await session.execute(select(Siswa).filter(Siswa.id == id_siswa))).scalar_one_or_none()
    if not findSiswa :
        raise HttpException(404,"siswa tidak ditemukan")
    
    if findSiswa.status != StatusPKLEnum.sudah_pkl or not findSiswa.id_dudi :
        raise HttpException(400,"siswa belum memiliki tempat pkl")
    
    pengajuanCancelMapping = {
        "id" : random_strings.random_digits(6),
        "id_siswa" : id_siswa,
        "id_dudi" : findSiswa.id_dudi,
        "status" : StatusCancelPKLENUM.proses.value,
        "waktu_pengajuan" : datetime.utcnow()
    }

    siswaDictCopy = deepcopy(findSiswa.__dict__)
    session.add(PengajuanCancelPKL(**pengajuanCancelMapping))
    await session.commit()

    # Menjalankan addNotif dalam proses terpisah
    proccess = Process(target=runningProccessSync,args=(pengajuanCancelMapping["id_dudi"],siswaDictCopy["nama"]))
    proccess.start()

    return {
        "msg" : "success",
        "data" : pengajuanCancelMapping
    }
        
async def getAllPengajuanCancelPkl(id_siswa : int,status : StatusCancelPKLENUM | None,session : AsyncSession) -> PengajuanCancelPklWithDudi :
    findPengajuanCancelPkl = (await session.execute(select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.dudi)).filter(and_(PengajuanCancelPKL.id_siswa == id_siswa,PengajuanCancelPKL.status == status if status else True)))).scalars().all()
    
    return {
        "msg" : "success",
        "data" : findPengajuanCancelPkl
    }

async def cancelPengjuan(id_siswa : int,id_pengajuan : int,session : AsyncSession) -> PengajuanCancelPklWithDudi :
    findPengajuanCancelPkl = (await session.execute(select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.dudi)).filter(and_(PengajuanCancelPKL.id == id_pengajuan,PengajuanCancelPKL.id_siswa == id_siswa)))).scalar_one_or_none()
    
    if not findPengajuanCancelPkl :
        raise HttpException(404,"pengajuan cancel pkl tidak ditemukan")
    
    if findPengajuanCancelPkl.status != StatusCancelPKLENUM.proses :
        raise HttpException(400,"hanya pengajuan cancel pkl yang sedang diproses yang bisa di cancel")
    
    findPengajuanCancelPkl.status = StatusCancelPKLENUM.dibatalkan.value
    pengajuanDict = deepcopy(findPengajuanCancelPkl.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : findPengajuanCancelPkl
    }

async def getPengajuanCancelPklById(id_siswa : int,id_pengajuan : int,session : AsyncSession) -> PengajuanCancelPklWithDudi :
    findPengajuanCancelPkl = (await session.execute(select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.dudi)).filter(and_(PengajuanCancelPKL.id == id_pengajuan,PengajuanCancelPKL.id_siswa == id_siswa)))).scalar_one_or_none()
    
    if not findPengajuanCancelPkl :
        raise HttpException(404,"pengajuan cancel pkl tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPengajuanCancelPkl
    }

async def getLastPengajuanCancelPkl(id_siswa : int,session : AsyncSession) -> PengajuanCancelPklWithDudi :
    findPengajuanCancelPkl = (await session.execute(select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.dudi)).filter(PengajuanCancelPKL.id_siswa == id_siswa).order_by(PengajuanCancelPKL.waktu_pengajuan.desc()).limit(1))).scalar_one_or_none()
    
    if not findPengajuanCancelPkl :
        raise HttpException(404,"pengajuan cancel pkl kosong")
    
    return {
        "msg" : "success",
        "data" : findPengajuanCancelPkl
    }