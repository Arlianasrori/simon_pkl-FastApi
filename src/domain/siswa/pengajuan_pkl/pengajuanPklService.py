import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, select,and_,func
from sqlalchemy.orm import joinedload

# models
from ...models_domain.pengajuan_pkl_model import PengajuanPklWithDudi
from ....models.pengajuanPklModel import PengajuanPKL,StatusPengajuanENUM
from ....models.siswaModel import Siswa,StatusPKLEnum
from .pengajuanPklModel import AddPengajuanPklBody,CancelPengajuanBody
from ....models.dudiModel import Dudi,KuotaSiswa, KuotaSiswaByJurusan
from ....models.siswaModel import JenisKelaminEnum

# common
from ....error.errorHandling import HttpException
from python_random_strings import random_strings
from copy import deepcopy
from datetime import datetime
from multiprocessing import Process

# notif
from ..notification.notifUtils import runningProccessSync


async def addPengajuanPkl(id_siswa : int,id_sekolah : int,pengajuan : AddPengajuanPklBody,session : AsyncSession) -> PengajuanPklWithDudi :
    findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id_siswa))).scalar_one_or_none()

    if not findSiswa :
        raise HttpException(404,"siswa tidak ditemukan")
    
    if findSiswa.status == StatusPKLEnum.sudah_pkl :
        raise HttpException(400,"siswa tidak dapat melakukan pengjuan,karena siswa sudah pkl")
    
    # get last pengajuan siswa
    lastPengajuanSiswa = (await session.execute(select(PengajuanPKL).where(PengajuanPKL.id_siswa == id_siswa).order_by(PengajuanPKL.waktu_pengajuan.desc()).limit(1))).scalar_one_or_none()

    # validasi apakah siswa apakah pengajuan sebelumnya sedang diproses
    if lastPengajuanSiswa :
        if lastPengajuanSiswa.status == StatusPengajuanENUM.proses :
            raise HttpException(400,"siswa tidak dapat melakukan pengajuan,karena siswa sedang menunggu konfirmasi pengjuan sebelumnya,silahkan batalkan pengajuan sebelumnya untuk melakukan pengajuan baru")

    # validasi apakah dudi yang ingin diajukan ada
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kuota).subqueryload(KuotaSiswa.kuota_jurusan).joinedload(KuotaSiswaByJurusan.jurusan)).where(and_(Dudi.id == pengajuan.id_dudi,Dudi.id_sekolah == id_sekolah)))).scalar_one_or_none()
    if not findDudi :
        raise HttpException(404,"dudi yang ingin diajukan tidak ditemukan")

    # validasi apakah dudi memiliki kuota
    if not findDudi.kuota :
        raise HttpException(400,"dudi belum tersedia dan tidak dapat melakukan pengajuan")

    # Dapatkan jumlah siswa pria dan wanita yang sudah terdaftar pada dudi
    jumlah_siswa = (await session.execute(
        select(
            func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.laki).label('jumlah_pria'),
            func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.perempuan).label('jumlah_wanita'),
        ).where(Siswa.id_dudi == findDudi.id)
    )).one()

    jumlahSiswaPria = jumlah_siswa.jumlah_pria or 0
    jumlahSiswaWanita = jumlah_siswa.jumlah_wanita or 0

    # validasi jka jumlah siswa mereturn None
    jumlahSiswaPria = jumlahSiswaPria if jumlahSiswaPria else 0
    jumlahSiswaWanita = jumlahSiswaWanita if jumlahSiswaWanita else 0

    if not findDudi :
        raise HttpException(404,"dudi tidak ditemukan")
    
    if findDudi.id_tahun != findSiswa.id_tahun :
        raise HttpException(400,"dudi tidak ditemukan")

    if (jumlahSiswaPria + jumlahSiswaWanita >= findDudi.kuota.jumlah_pria + findDudi.kuota.jumlah_wanita):
        raise HttpException(400,"kuota dudi sudah penuh")
    
    if findSiswa.jenis_kelamin == JenisKelaminEnum.laki and findDudi.kuota.jumlah_pria != 0:
        if jumlahSiswaPria + 1 > findDudi.kuota.jumlah_pria:
            raise HttpException(400,"kuota dudi sudah penuh")
    elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and findDudi.kuota.jumlah_wanita != 0:
        if jumlahSiswaWanita + 1 > findDudi.kuota.jumlah_wanita:
            raise HttpException(400,"kuota dudi sudah penuh")

    totalKebutuhanLaki = 0
    totalKebutuhanWanita = 0
    totalSiswaLakiAlljurusan = 0
    totalSiswaWanitaAlljurusan = 0
    lolosSeleksiJurusan = False
    for kuota_jurusan in findDudi.kuota.kuota_jurusan:      
        countDudiBykuota = (await session.execute(select(
                func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.laki).label("jumlah_siswa_pria"),
                func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.perempuan).label("jumlah_siswa_wanita"),
                ).where(
                    and_(
                        Siswa.id_jurusan == kuota_jurusan.id_jurusan,
                        Siswa.id_dudi == pengajuan.id_dudi
                    )
                ))).one()._asdict()
        
        countDudiBykuota["jumlah_siswa_pria"] = countDudiBykuota["jumlah_siswa_pria"] if countDudiBykuota["jumlah_siswa_pria"] else 0
        countDudiBykuota["jumlah_siswa_wanita"] = countDudiBykuota["jumlah_siswa_wanita"] if countDudiBykuota["jumlah_siswa_wanita"] else 0

        totalKebutuhanLaki += kuota_jurusan.jumlah_pria
        totalKebutuhanWanita += kuota_jurusan.jumlah_wanita
        totalSiswaLakiAlljurusan += countDudiBykuota["jumlah_siswa_pria"]
        totalSiswaWanitaAlljurusan += countDudiBykuota["jumlah_siswa_wanita"]
        if kuota_jurusan.id_jurusan == findSiswa.id_jurusan:
            if findSiswa.jenis_kelamin == JenisKelaminEnum.laki and findDudi.kuota.jumlah_pria != 0:
                if countDudiBykuota["jumlah_siswa_pria"] + 1 > kuota_jurusan.jumlah_pria:
                    raise HttpException(400,"kuota dudi sudah penuh")
            elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and findDudi.kuota.jumlah_wanita != 0:
                if countDudiBykuota["jumlah_siswa_wanita"] + 1 > kuota_jurusan.jumlah_wanita:
                    raise HttpException(400,"kuota dudi sudah penuh")
        lolosSeleksiJurusan = True

    kebutuhanJurusanLaki = totalKebutuhanLaki - totalSiswaLakiAlljurusan
    kebutuhanJurusanWanita = totalKebutuhanWanita - totalSiswaWanitaAlljurusan

    sisaKuotaDudiPria = findDudi.kuota.jumlah_pria - jumlahSiswaPria
    sisaKuotaDudiWanita = findDudi.kuota.jumlah_wanita - jumlahSiswaWanita

    if not lolosSeleksiJurusan :
        if findSiswa.jenis_kelamin == JenisKelaminEnum.laki :
            if sisaKuotaDudiPria <= kebutuhanJurusanLaki :
                raise HttpException(400,"kuota dudi sudah penuh")
        elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan :
            if sisaKuotaDudiWanita <= kebutuhanJurusanWanita :
                raise HttpException(400,"kuota dudi sudah penuh")
            
    pengjuanPklMapping = pengajuan.model_dump()
    pengjuanPklMapping.update({"id" : random_strings.random_digits(6),"id_siswa":id_siswa,"status" : StatusPengajuanENUM.proses.value,"waktu_pengajuan" : datetime.utcnow()})

    dudiDictCopy = deepcopy(findDudi.__dict__)
    siswaDictCopy = deepcopy(findSiswa.__dict__)
    session.add(PengajuanPKL(**pengjuanPklMapping))
    findSiswa.status = StatusPKLEnum.menunggu.value
    await session.commit()

    # Menjalankan addNotif dalam proses terpisah
    proccess = Process(target=runningProccessSync,args=(pengajuan.id_dudi,siswaDictCopy["nama"]))
    proccess.start()

    return {
        "msg" : "success",
        "data" : {
            **pengjuanPklMapping,
            "dudi" : dudiDictCopy
        }
    }

async def cancelPengajuanPkl(id_siswa : int,id_pengajuan : int,body : CancelPengajuanBody,session : AsyncSession) -> PengajuanPklWithDudi :
    findPengjuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.dudi),joinedload(PengajuanPKL.siswa)).filter(and_(PengajuanPKL.id == id_pengajuan,PengajuanPKL.id_siswa == id_siswa)))).scalar_one_or_none()
    print(findPengjuanPkl.__dict__)
    if not findPengjuanPkl :
        raise HttpException(404,"pengajuan tidak ditemukan")
    if findPengjuanPkl.status != StatusPengajuanENUM.proses :
        raise HttpException(400,"hanya pengajuan yang sedang diproses yang boleh dibatalkan")
    
    findPengjuanPkl.status = StatusPengajuanENUM.dibatalkan.value
    findPengjuanPkl.alasan_pembatalan = body.alasan
    findPengjuanPkl.siswa.status = StatusPKLEnum.belum_pkl.value
    pengjuanDictCopy = deepcopy(findPengjuanPkl.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : pengjuanDictCopy
    }
    
    

async def getAllPengajuanPkl(id_siswa : int,status : StatusPengajuanENUM | None,session : AsyncSession) -> list[PengajuanPklWithDudi] :
    findPengjuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.dudi)).filter(and_(PengajuanPKL.id_siswa == id_siswa,PengajuanPKL.status == status if status else True)).order_by(PengajuanPKL.waktu_pengajuan.desc()))).scalars().all()

    return {
        "msg" : "success",
        "data" : findPengjuanPkl
    }

async def getPengajuanPklById(id_siswa : int,id_pengajuan : int,session : AsyncSession) -> PengajuanPklWithDudi :
    findPengjuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.dudi)).filter(and_(PengajuanPKL.id == id_pengajuan,PengajuanPKL.id_siswa == id_siswa)))).scalar_one_or_none()

    if not findPengjuanPkl :
        raise HttpException(404,"pengajuan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPengjuanPkl
    }

async def getLastPengajuanPkl(id_siswa : int,session : AsyncSession) -> PengajuanPklWithDudi :
    findPengjuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.dudi)).filter(PengajuanPKL.id_siswa == id_siswa).order_by(PengajuanPKL.waktu_pengajuan.desc()).limit(1))).scalar_one_or_none()
    print(findPengjuanPkl)

    if not findPengjuanPkl :
        raise HttpException(404,"pengajuan tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPengjuanPkl
    }