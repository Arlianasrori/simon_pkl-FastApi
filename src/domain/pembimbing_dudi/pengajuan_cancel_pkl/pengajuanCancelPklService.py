from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, desc, select,func,and_
from sqlalchemy.orm import joinedload

# models
from .pengajuanCancelPklModel import ResponsePengajuanCancelPklPag,AccPengajuanEnum,AccDccPengajuanPkl
from ...models_domain.pengajuan_cancel_pkl_model import PengajuanCancelPklWithSiswa
from ....models.pengajuanPklModel import PengajuanCancelPKL,StatusCancelPKLENUM
from ....models.siswaModel import StatusPKLEnum

# common
from ....error.errorHandling import HttpException
import math

from multiprocessing import Process

# notification
from ..notification_pembimbing_dudi.notificationUtils import runningProccessSync

async def getAllPengajuancancelPkl(id_dudi : int,page : int | None,session : AsyncSession) -> list[PengajuanCancelPklWithSiswa] | ResponsePengajuanCancelPklPag :
    statementSelectPengajuanPkl = select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.siswa)).where(PengajuanCancelPKL.id_dudi == id_dudi)
    
    if page :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl.limit(10).offset(10 * (page - 1)).order_by(case((PengajuanCancelPKL.status == StatusCancelPKLENUM.proses, 1)),desc(PengajuanCancelPKL.waktu_pengajuan)))).scalars().all()
        countData = (await session.execute(func.count(PengajuanCancelPKL.id))).scalar_one()
        countPage = math.ceil(countData / 10)
        return {
            "msg" : "success",
            "data" : findPengajuanPkl,
            "count_data" : countData,
            "count_page" : countPage
        }
    else :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl.order_by(case((PengajuanCancelPKL.status == StatusCancelPKLENUM.proses, 1)),desc(PengajuanCancelPKL.waktu_pengajuan)))).scalars().all()
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
    findPengajuanPkl = (await session.execute(select(PengajuanCancelPKL).options(joinedload(PengajuanCancelPKL.siswa),joinedload(PengajuanCancelPKL.dudi)).where(and_(PengajuanCancelPKL.id == id_pengajuan_cancel_pkl,PengajuanCancelPKL.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findPengajuanPkl :
        raise HttpException(404,"pengajuan pkl tidak ditemukan")
    
    if findPengajuanPkl.status != StatusCancelPKLENUM.proses :
        raise HttpException(400,"pengajuan cancel telah diproses")
    
    # notif
    mappingForNotif = {
        "id_siswa" : findPengajuanPkl.siswa.id,
    }
    # lanjutin store to datrabase
    if pengajuan_pkl.status == AccPengajuanEnum.SETUJU :
        findPengajuanPkl.status = StatusCancelPKLENUM.setuju.value
        findPengajuanPkl.siswa.status = StatusPKLEnum.belum_pkl.value
        findPengajuanPkl.siswa.id_dudi = None
        findPengajuanPkl.siswa.id_pembimbing_dudi = None

        # notif
        mappingForNotif["title"] = "Kabar Baik UntukMu!"
        mappingForNotif["body"] = f"Ajuan Untuk Keluar PKL Mu Telah Disetujui Oleh {findPengajuanPkl.dudi.nama_instansi_perusahaan}"

        print("setuju")
    elif pengajuan_pkl.status == AccPengajuanEnum.TIDAK_SETUJU :
        findPengajuanPkl.status = StatusCancelPKLENUM.tidak_setuju.value

        # notif
        mappingForNotif["title"] = "Informasi UntukMu!!"
        mappingForNotif["body"] = f"Ajuan Pkl Mu Tidak Disetujui Oleh {findPengajuanPkl.dudi.nama_instansi_perusahaan}"
        print("tidak setuju")
    
    pengajuanDictCopy = deepcopy(findPengajuanPkl)
    id_pengajuan = deepcopy(findPengajuanPkl.id)
    
    await session.commit()

    # Menjalankan addNotif dalam proses terpisah
    proccess = Process(target=runningProccessSync,args=(mappingForNotif["id_siswa"],mappingForNotif["title"],mappingForNotif["body"],id_pengajuan))
    proccess.start()

    return {
        "msg" : "success",
        "data" : pengajuanDictCopy
    }