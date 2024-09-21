import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, select,and_,func
from sqlalchemy.orm import joinedload

# models
from ...models_domain.pengajuan_pkl_model import PengajuanPklWithDudi
from ....models.pengajuanPklModel import PengajuanPKL,StatusPengajuanENUM
from ....models.siswaModel import Siswa,StatusPKLEnum
from .pengajuanPklModel import AddPengajuanPklBody
from ....models.dudiModel import Dudi,KoutaSiswa
from ....models.siswaModel import JenisKelaminEnum

# common
from ....error.errorHandling import HttpException
from python_random_strings import random_strings
from copy import deepcopy
from datetime import datetime


async def addPengajuanPkl(id_siswa : int,id_sekolah : int,pengajuan : AddPengajuanPklBody,session : AsyncSession) -> PengajuanPklWithDudi :
    findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id_siswa))).scalar_one_or_none()

    if not findSiswa :
        raise HttpException(404,"siswa tidak ditemukan")
    
    if findSiswa.status == StatusPKLEnum.sudah_pkl :
        raise HttpException(400,"siswa tidak dapat melakukan pengjuan,karena siswa sudah pkl")
    
    lastPengajuanSiswa = (await session.execute(select(PengajuanPKL).where(PengajuanPKL.id_siswa == id_siswa).order_by(PengajuanPKL.waktu_pengajuan.desc()).limit(1))).scalar_one_or_none()

    print(lastPengajuanSiswa)
    if lastPengajuanSiswa :
        if lastPengajuanSiswa.status == StatusPengajuanENUM.proses :
            raise HttpException(400,"siswa tidak dapat melakukan pengjuan,karena siswa sedang menunggu konfirmasi pengjuan sebelumnya,silahkan batalkan pengajuan sebelumnya untuk melakukan pengajuan baru")

    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta).subqueryload(KoutaSiswa.kouta_jurusan)).where(and_(Dudi.id == pengajuan.id_dudi,Dudi.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"dudi yang ingin diajukan tidak ditemukan")

    jumlahSiswaPria = (await session.execute(select(func.count(Siswa.id)).where(and_(Siswa.id_dudi == findDudi.id,Siswa.jenis_kelamin == JenisKelaminEnum.laki)))).scalar_one()
    jumlahSiswaWanita = (await session.execute(select(func.count(Siswa.id)).where(and_(Siswa.id_dudi == findDudi.id,Siswa.jenis_kelamin == JenisKelaminEnum.perempuan)))).scalar_one()

    if not findDudi :
        raise HttpException(404,"dudi tidak ditemukan")
    
    if findDudi.id_tahun != findSiswa.id_tahun :
        raise HttpException(400,"dudi tidak ditemukan")

    if (jumlahSiswaPria + jumlahSiswaWanita >= findDudi.kouta.jumlah_pria + findDudi.kouta.jumlah_wanita):
        raise HttpException(400,"kouta dudi sudah penuh")
    
    if findSiswa.jenis_kelamin == JenisKelaminEnum.laki and findDudi.kouta.jumlah_pria != 0:
        if jumlahSiswaPria + 1 > findDudi.kouta.jumlah_pria:
            raise HttpException(400,"kouta dudi sudah penuh")
    elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and findDudi.kouta.jumlah_wanita != 0:
        if jumlahSiswaWanita + 1 > findDudi.kouta.jumlah_wanita:
            raise HttpException(400,"kouta dudi sudah penuh")
    
    for kouta_jurusan in findDudi.kouta.kouta_jurusan:
        if kouta_jurusan.id_jurusan == findSiswa.id_jurusan:
            countDudiBykouta = (await session.execute(select(
                        func.count(case((Siswa.jenis_kelamin == JenisKelaminEnum.laki, 1), else_=0)).label("jumlah_siswa_pria"),
                        func.count(case((Siswa.jenis_kelamin == JenisKelaminEnum.perempuan, 1), else_=0)).label("jumlah_siswa_wanita")
                    ).where(
                        and_(
                            Siswa.id_jurusan == kouta_jurusan.id_jurusan,
                            Siswa.id_dudi == pengajuan.id_dudi
                        )
                    ))).one()._asdict()
            print(countDudiBykouta)
            if findSiswa.jenis_kelamin == JenisKelaminEnum.laki and findDudi.kouta.jumlah_pria != 0:
                if countDudiBykouta["jumlah_siswa_pria"] + 1 > kouta_jurusan.jumlah_pria:
                    raise HttpException(400,"kouta dudi sudah penuh")
            elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and findDudi.kouta.jumlah_wanita != 0:
                if countDudiBykouta["jumlah_siswa_wanita"] + 1 > kouta_jurusan.jumlah_wanita:
                    raise HttpException(400,"kouta dudi sudah penuh")
                
    pengjuanPklMapping = pengajuan.model_dump()
    pengjuanPklMapping.update({"id" : random_strings.random_digits(6),"id_siswa":id_siswa,"status" : StatusPengajuanENUM.proses.value,"waktu_pengajuan" : datetime.utcnow()})

    dudiDictCopy = deepcopy(findDudi.__dict__)

    session.add(PengajuanPKL(**pengjuanPklMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : {
            **pengjuanPklMapping,
            "dudi" : dudiDictCopy
        }
    }

async def cancelPengajuanPkl(id_siswa : int,id_pengajuan : int,session : AsyncSession) -> PengajuanPklWithDudi :
    findPengjuanPkl = (await session.execute(select(PengajuanPKL).options(joinedload(PengajuanPKL.dudi)).filter(and_(PengajuanPKL.id == id_pengajuan,PengajuanPKL.id_siswa == id_siswa)))).scalar_one_or_none()
    print(findPengjuanPkl.__dict__)
    if not findPengjuanPkl :
        raise HttpException(404,"pengajuan tidak ditemukan")
    if findPengjuanPkl.status != StatusPengajuanENUM.proses :
        raise HttpException(400,"hanya pengajuan yang sedang diproses yang boleh dibatalkan")
    
    findPengjuanPkl.status = StatusPengajuanENUM.dibatalkan.value
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