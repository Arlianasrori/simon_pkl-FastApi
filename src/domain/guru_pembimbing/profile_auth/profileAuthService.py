from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

# models
from ...models_domain.guru_pembimbing_model import GuruPembimbingBase,GuruPembimbingWithSekolahAlamat
from ....models.guruPembimbingModel import GuruPembimbing

# common 
from ....error.errorHandling import HttpException

async def getGuruPembimbing(id_guru_pembimbing : int,session : AsyncSession) -> GuruPembimbingBase :
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == id_guru_pembimbing))).scalar_one_or_none()

    if not findGuruPembimbing :
        raise HttpException(404,"guru pembimbing tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findGuruPembimbing
    }

async def getProfileAuth(id_guru_pembimbing : int,session : AsyncSession) -> GuruPembimbingWithSekolahAlamat :
    findGuruPembimbing = (await session.execute(select(GuruPembimbing).options(joinedload(GuruPembimbing.alamat),joinedload(GuruPembimbing.sekolah)).where(GuruPembimbing.id == id_guru_pembimbing))).scalar_one_or_none()

    if not findGuruPembimbing :
        raise HttpException(404,"guru pembimbing tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findGuruPembimbing
    }

