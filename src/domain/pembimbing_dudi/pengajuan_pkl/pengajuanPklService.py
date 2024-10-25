from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, desc, select,func,and_
from sqlalchemy.orm import joinedload

# models
from .pengajuanPklModel import ResponsePengajuanPklPag,AccDccPengajuanPkl,AccPengajuanEnum,EnumForAllPengjuan,ResponseGroupingPengajuanPag,ResponseGroupingPengajuan
from ...models_domain.pengajuan_pkl_model import PengajuanPklWithSiswa,PengajuanPklWithSiswaJurusanKelas
from ....models.pengajuanPklModel import PengajuanPKL,StatusPengajuanENUM
from ....models.siswaModel import StatusPKLEnum
from ....models.siswaModel import Siswa

# common
from ....error.errorHandling import HttpException
import math

from multiprocessing import Process

# notification
from ..notification_pembimbing_dudi.notificationUtils import runningProccessSync

async def getAllPengajuanPkl(id_dudi : int,page : int | None,usingGrouping : bool,session : AsyncSession) -> list[PengajuanPklWithSiswaJurusanKelas] | ResponsePengajuanPklPag | ResponseGroupingPengajuanPag | ResponseGroupingPengajuan:
    statementSelectPengajuanPkl = select(PengajuanPKL).options(joinedload(PengajuanPKL.siswa).options(joinedload(Siswa.jurusan),joinedload(Siswa.kelas),joinedload(Siswa.alamat))).where(PengajuanPKL.id_dudi == id_dudi)

    if page :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl.limit(10).offset(10 * (page - 1)).order_by(case((PengajuanPKL.status == StatusPengajuanENUM.proses, 1)),desc(PengajuanPKL.waktu_pengajuan)))).scalars().all()
        countData = (await session.execute(func.count(PengajuanPKL.id))).scalar_one()
        countPage = math.ceil(countData / 10)

        if usingGrouping :
            responsePengajuan = {
                EnumForAllPengjuan.MENUNGGU_VERIFIKASI.value : [],
                EnumForAllPengjuan.DIBATALKAN.value : [],
                EnumForAllPengjuan.VERIFIKASI_SELESAI.value : []
            }
            for pengajuan in findPengajuanPkl :
                if pengajuan.status == StatusPengajuanENUM.proses :
                    responsePengajuan[EnumForAllPengjuan.MENUNGGU_VERIFIKASI.value].append(pengajuan)
                elif pengajuan.status == StatusPengajuanENUM.dibatalkan :
                    responsePengajuan[EnumForAllPengjuan.DIBATALKAN.value].append(pengajuan)
                else :
                    responsePengajuan[EnumForAllPengjuan.VERIFIKASI_SELESAI.value].append(pengajuan)
        else :
            responsePengajuan = findPengajuanPkl
        
        print(responsePengajuan)
        return {
            "msg" : "success",
            "data" : responsePengajuan,
            "count_data" : countData,
            "count_page" : countPage
        }
    else :
        findPengajuanPkl = (await session.execute(statementSelectPengajuanPkl.order_by(case((PengajuanPKL.status == StatusPengajuanENUM.proses, 1)),desc(PengajuanPKL.waktu_pengajuan)))).scalars().all()

        if usingGrouping :
            print("hay")
            responsePengajuan = {
                EnumForAllPengjuan.MENUNGGU_VERIFIKASI.value : [],
                EnumForAllPengjuan.DIBATALKAN.value : [],
                EnumForAllPengjuan.VERIFIKASI_SELESAI.value : []
            }
            for pengajuan in findPengajuanPkl :
                if pengajuan.status == StatusPengajuanENUM.proses :
                    responsePengajuan[EnumForAllPengjuan.MENUNGGU_VERIFIKASI.value].append(pengajuan)
                elif pengajuan.status == StatusPengajuanENUM.dibatalkan :
                    responsePengajuan[EnumForAllPengjuan.DIBATALKAN.value].append(pengajuan)
                else :
                    responsePengajuan[EnumForAllPengjuan.VERIFIKASI_SELESAI.value].append(pengajuan)
        else :
            responsePengajuan = findPengajuanPkl

        return {
            "msg" : "success",
            "data" : responsePengajuan
        }

async def getPengajuanPklById(id_pengajuan_pkl : int,id_dudi : int,session : AsyncSession) -> PengajuanPklWithSiswaJurusanKelas :
    findPengajuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.siswa).options(joinedload(Siswa.jurusan),joinedload(Siswa.kelas),joinedload(Siswa.alamat))).where(and_(PengajuanPKL.id == id_pengajuan_pkl,PengajuanPKL.id_dudi == id_dudi)))).scalar_one_or_none()

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
        findPengajuanPkl.siswa.status = StatusPKLEnum.belum_pkl.value

        # notif
        mappingForNotif["title"] = "Informasi UntukMu!!"
        mappingForNotif["body"] = f"Ajuan Pkl Mu DiTolak Oleh {findPengajuanPkl.dudi.nama_instansi_perusahaan}"
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