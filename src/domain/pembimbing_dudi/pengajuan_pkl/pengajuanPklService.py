from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, desc, select,func,and_
from sqlalchemy.orm import joinedload

# models
from .pengajuanPklModel import ResponsePengajuanPklPag,AccDccPengajuanPkl,AccPengajuanEnum
from ...models_domain.pengajuan_pkl_model import PengajuanPklWithSiswa
from ....models.pengajuanPklModel import PengajuanPKL,StatusPengajuanENUM
from ....models.siswaModel import StatusPKLEnum

# common
from ....error.errorHandling import HttpException
import math

from multiprocessing import Process

# notification
from ..notification.notificationUtils import runningProccessSync

async def getAllPengajuanPkl(id_dudi : int,page : int | None,session : AsyncSession) -> list[PengajuanPklWithSiswa] | ResponsePengajuanPklPag :
    statementSelectPengajuanPkl = select(PengajuanPKL).options(joinedload(PengajuanPKL.siswa)).where(PengajuanPKL.id_dudi == id_dudi)

    if page :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl.limit(10).offset(10 * (page - 1)).order_by(case((PengajuanPKL.status == StatusPengajuanENUM.proses, 1)),desc(PengajuanPKL.waktu_pengajuan)))).scalars().all()
        countData = (await session.execute(func.count(PengajuanPKL.id))).scalar_one()
        countPage = math.ceil(countData / 10)
        return {
            "msg" : "success",
            "data" : findPengajuanPkl,
            "count_data" : countData,
            "count_page" : countPage
        }
    else :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl.order_by(case((PengajuanPKL.status == StatusPengajuanENUM.proses, 1)),desc(PengajuanPKL.waktu_pengajuan)))).scalars().all()
        return {
            "msg" : "success",
            "data" : findPengajuanPkl
        }

async def getPengajuanPklById(id_pengajuan_pkl : int,id_dudi : int,session : AsyncSession) -> PengajuanPklWithSiswa :
    findPengajuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.siswa)).where(and_(PengajuanPKL.id == id_pengajuan_pkl,PengajuanPKL.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findPengajuanPkl :
        raise HttpException(404,"Pengajuan PKL tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPengajuanPkl
    }

async def accDccPengajuanPkl(id_pengajuan_pkl : int,id_pembimbing: int,id_dudi : int,pengajuan_pkl : AccDccPengajuanPkl,session : AsyncSession) -> PengajuanPklWithSiswa :
    findPengajuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.siswa),joinedload(PengajuanPKL.dudi)).where(and_(PengajuanPKL.id == id_pengajuan_pkl,PengajuanPKL.id_dudi == id_dudi)))).scalar_one_or_none()

    if not findPengajuanPkl :
        raise HttpException(404,"pengajuan pkl tidak ditemukan")
    
    if findPengajuanPkl.status != StatusPengajuanENUM.proses :
        raise HttpException(400,"pengajuan telah diproses")
    
    # lanjutin store to dataabase
    mappingForNotif = {
        "id_siswa" : findPengajuanPkl.siswa.id,
    }
    print(pengajuan_pkl.status)
    if pengajuan_pkl.status ==  AccPengajuanEnum.SETUJU:
        print("tes")
        findPengajuanPkl.status = StatusPengajuanENUM.diterima.value
        findPengajuanPkl.siswa.status = StatusPKLEnum.sudah_pkl.value
        findPengajuanPkl.siswa.id_dudi = findPengajuanPkl.id_dudi
        findPengajuanPkl.siswa.id_pembimbing_dudi = id_pembimbing

        # notif
        mappingForNotif["title"] = "Kabar Baik UntukMu!"
        mappingForNotif["body"] = f"Ajuan Pkl Mu Telah Diterima Oleh {findPengajuanPkl.dudi.nama_instansi_perusahaan}"
        print("setuju")
    elif pengajuan_pkl.status == AccPengajuanEnum.TIDAK_SETUJU :
        findPengajuanPkl.status = StatusPengajuanENUM.ditolak.value

        # notif
        mappingForNotif["title"] = "Informasi UntukMu!!"
        mappingForNotif["body"] = f"Ajuan Pkl Mu DiTolak Oleh {findPengajuanPkl.dudi.nama_instansi_perusahaan}"
        print("tidak setuju")
    
    pengajuanDictCopy = deepcopy(findPengajuanPkl)
    await session.commit()

    # Menjalankan addNotif dalam proses terpisah
    proccess = Process(target=runningProccessSync,args=(mappingForNotif["id_siswa"],mappingForNotif["title"],mappingForNotif["body"]))
    proccess.start()

    return {
        "msg" : "success",
        "data" : pengajuanDictCopy
    }