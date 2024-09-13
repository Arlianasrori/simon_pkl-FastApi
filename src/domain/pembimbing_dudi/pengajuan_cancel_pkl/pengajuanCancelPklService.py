from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,and_
from sqlalchemy.orm import joinedload

# models
from .pengajuanCancelPklModel import ResponsePengajuanCancelPklPag,AccPengajuanEnum,AccDccPengajuanPkl
from ...models_domain.pengajuan_cancel_pkl_model import PengajuanCancelPklWithSiswa
from ....models.pengajuanPklModel import PengajuanCancelPKL,StatusCancelPKLENUM
from ....models.siswaModel import StatusPKLEnum

# common
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable
import math

async def getAllPengajuancancelPkl(id_dudi : int,page : int | None,session : AsyncSession) -> list[PengajuanCancelPklWithSiswa] | ResponsePengajuanCancelPklPag :
    statementSelectPengajuanPkl = select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.siswa)).where(PengajuanCancelPKL.id_dudi == id_dudi)

    if page :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl.limit(10).offset(10 * (page - 1)))).scalars().all()
        countData = (await session.execute(func.count(PengajuanCancelPKL.id))).scalar_one()
        countPage = math.ceil(countData / 10)
        return {
            "msg" : "success",
            "data" : findPengajuanPkl,
            "count_data" : countData,
            "count_page" : countPage
        }
    else :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl)).scalars().all()
        return {
            "msg" : "success",
            "data" : findPengajuanPkl
        }

async def getPengajuanCancelPklById(id_pengajuan_pkl : int,id_dudi : int,session : AsyncSession) -> PengajuanCancelPklWithSiswa :
    findPengajuanPkl = (await session.execute(select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.siswa)).where(and_(PengajuanCancelPKL.id == id_pengajuan_pkl,PengajuanCancelPKL.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findPengajuanPkl :
        raise HttpException(404,"Pengajuan PKL tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPengajuanPkl
    }

async def accDccPengajuanPkl(id_pengajuan_cancel_pkl : int,id_dudi : int,pengajuan_pkl : AccDccPengajuanPkl,session : AsyncSession) -> PengajuanCancelPklWithSiswa :
    findPengajuanPkl = (await session.execute(select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.siswa)).where(and_(PengajuanCancelPKL.id == id_pengajuan_cancel_pkl,PengajuanCancelPKL.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findPengajuanPkl :
        raise HttpException(404,"pengajuan pkl tidak ditemukan")
    
    if findPengajuanPkl.status != StatusCancelPKLENUM.proses :
        raise HttpException(400,"pengajuan cancel telah diproses")
    
    # lanjutin store to datrabase
    if pengajuan_pkl.status == AccPengajuanEnum.SETUJU :
        findPengajuanPkl.status = StatusCancelPKLENUM.setuju.value
        findPengajuanPkl.siswa.status = StatusPKLEnum.belum_pkl.value
        findPengajuanPkl.siswa.id_dudi = None
        findPengajuanPkl.siswa.id_pembimbing_dudi = None
        print("setuju")
    elif pengajuan_pkl.status == AccPengajuanEnum.TIDAK_SETUJU :
        findPengajuanPkl.status = StatusCancelPKLENUM.tidak_setuju.value
        print("tidak setuju")
    
    pengajuanDictCopy = deepcopy(findPengajuanPkl)
    await session.commit()

    return {
        "msg" : "success",
        "data" : pengajuanDictCopy
    }
