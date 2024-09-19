import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,case,and_
from sqlalchemy.orm import joinedload

# models
from .getDudiModel import FilterGetDudiQuery,ResponseGetDudiPag
from ....models.dudiModel import Dudi,KoutaSiswa,KoutaSiswaByJurusan
from ...models_domain.dudi_model import DudiWithAlamat
from ....models.siswaModel import Siswa
from ....models.types import JenisKelaminEnum

# common
from ....error.errorHandling import HttpException

async def getDudi(id_siswa : int,id_sekolah : int,page : int,filter : FilterGetDudiQuery,session : AsyncSession) -> ResponseGetDudiPag :
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.jurusan)).where(Siswa.id == id_siswa))).scalar_one_or_none()

    if not findSiswa :
        raise HttpException(404,f"Siswa dengan id {id_siswa} tidak ditemukan")
    
    # Subquery untuk menghitung jumlah siswa
    siswa_count = (
        select(
            Siswa.id_dudi,
            func.count(case((Siswa.jenis_kelamin == JenisKelaminEnum.laki, 1))).label("jumlah_siswa_pria"),
            func.count(case((Siswa.jenis_kelamin == JenisKelaminEnum.perempuan, 1))).label("jumlah_siswa_wanita"),
            func.count(Siswa.id).label("total_siswa")
        )
        .group_by(Siswa.id_dudi)
        .subquery()
    )
    
    findDudi = (await session.execute(select(Dudi,siswa_count.c.jumlah_siswa_pria,siswa_count.c.jumlah_siswa_wanita).outerjoin(siswa_count, Dudi.id == siswa_count.c.id_dudi).options(joinedload(Dudi.alamat),joinedload(Dudi.kouta).subqueryload(KoutaSiswa.kouta_jurusan).joinedload(KoutaSiswaByJurusan.jurusan)).where(and_(Dudi.nama_instansi_perusahaan.ilike(f"%{filter.nama_instansi_perusahaan}%") if filter.nama_instansi_perusahaan else True,Dudi.id_sekolah == id_sekolah)).limit(10).offset(10 * (page - 1)))).all()

    countData = (await session.execute(select(func.count()).where(and_(Dudi.nama_instansi_perusahaan.ilike(f"%{filter.nama_instansi_perusahaan}%") if filter.nama_instansi_perusahaan else True,Dudi.id_sekolah == id_sekolah)))).scalar_one()
    countPage = math.ceil(countData / 10)

    responseDudiList = []
    for dudi in findDudi :
        dudiDecode = dudi._asdict()
        dudiDictDecode = dudiDecode["Dudi"].__dict__

        dudiDict = {
            **dudiDictDecode,
            "jumlah_siswa_pria" : dudiDecode["jumlah_siswa_pria"] if dudiDecode["jumlah_siswa_pria"] else 0,
            "jumlah_siswa_wanita" : dudiDecode["jumlah_siswa_wanita"] if dudiDecode["jumlah_siswa_wanita"] else 0,
            "jumlah_kouta_pria" : dudiDecode["Dudi"].kouta.jumlah_pria,
            "jumlah_kouta_wanita" : dudiDecode["Dudi"].kouta.jumlah_wanita,
            "tersedia" : True
        }

        # cek apakah dudi sudah penuh
        if dudiDict["jumlah_siswa_pria"] +  dudiDict["jumlah_siswa_wanita"]>= dudiDictDecode["kouta"].jumlah_pria + dudiDictDecode["kouta"].jumlah_wanita :
            print(1)
            dudiDict["tersedia"] = False
        elif findSiswa.jenis_kelamin == JenisKelaminEnum.laki and  dudiDictDecode["kouta"].jumlah_pria != 0:
            if dudiDict["jumlah_siswa_pria"] + 1 > dudiDictDecode["kouta"].jumlah_pria :
                dudiDict["tersedia"] = False
        elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and  dudi["kouta"].jumlah_wanita != 0:
            if dudiDict["jumlah_siswa_wanita"] + 1 > dudi["kouta"].jumlah_wanita :
                dudiDict["tersedia"] = False

        koutaJurusanList = []
        totalKebutuhanLaki = 0
        totalKebutuhanWanita = 0
        totalSiswaLakiAlljurusan = 0
        totalSiswaWanitaAlljurusan = 0
        for kouta_jurusan in dudiDictDecode["kouta"].kouta_jurusan :     
            countDudiBykouta = (await session.execute(select(
                func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.laki).label("jumlah_siswa_pria"),
                func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.perempuan).label("jumlah_siswa_wanita"),
            ).where(
                and_(
                    Siswa.id_jurusan == kouta_jurusan.id_jurusan,
                    Siswa.id_dudi == dudiDict["id"]
                )
            ))).one()._asdict()

            totalKebutuhanLaki += kouta_jurusan.jumlah_pria
            totalKebutuhanWanita += kouta_jurusan.jumlah_wanita
            totalSiswaLakiAlljurusan += countDudiBykouta["jumlah_siswa_pria"]
            totalSiswaWanitaAlljurusan += countDudiBykouta["jumlah_siswa_wanita"]

            if kouta_jurusan.id_jurusan == findSiswa.jurusan.id :  
                if findSiswa.jenis_kelamin == JenisKelaminEnum.laki and kouta_jurusan.jumlah_pria != 0:
                    if countDudiBykouta["jumlah_siswa_pria"] + 1 > kouta_jurusan.jumlah_pria :
                        dudiDict["tersedia"] = False
                elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and kouta_jurusan.jumlah_wanita != 0:
                    if countDudiBykouta["jumlah_siswa_wanita"] + 1 > kouta_jurusan.jumlah_wanita :
                        dudiDict["tersedia"] = False
            
            koutaJurusanMapping = {
                "jurusan" : kouta_jurusan.jurusan.nama,
                "kouta_pria" : kouta_jurusan.jumlah_pria,
                "kouta_wanita" : kouta_jurusan.jumlah_wanita,
                "jumlah_siswa_pria" : countDudiBykouta["jumlah_siswa_pria"] if countDudiBykouta["jumlah_siswa_pria"] else 0,
                "jumlah_siswa_wanita" : countDudiBykouta["jumlah_siswa_wanita"] if countDudiBykouta["jumlah_siswa_wanita"] else 0
            }

            koutaJurusanList.append(koutaJurusanMapping)

        kebutuhanJurusanLaki = totalKebutuhanLaki - totalSiswaLakiAlljurusan
        kebutuhanJurusanWanita = totalKebutuhanWanita - totalSiswaWanitaAlljurusan

        sisaKoutaDudiPria = dudiDecode["Dudi"].kouta.jumlah_pria - dudiDecode["jumlah_siswa_pria"]
        sisaKoutaDudiWanita = dudiDecode["Dudi"].kouta.jumlah_wanita - dudiDecode["jumlah_siswa_wanita"]

        if findSiswa.jenis_kelamin == JenisKelaminEnum.laki :
            if sisaKoutaDudiPria <= kebutuhanJurusanLaki :
                dudiDict["tersedia"] = False
        elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan :
            if sisaKoutaDudiWanita <= kebutuhanJurusanWanita :
                dudiDict["tersedia"] = False

        dudiDict["kouta_jurusan"] = koutaJurusanList
        responseDudiList.append(dudiDict)

    return {
        "msg" : "success",
        "data" : {
            "data" : responseDudiList,
            "count_data" : len(responseDudiList),
            "count_page" : countPage
        }
    }

async def getDudiById(id_dudi : int,id_sekolah : int,session : AsyncSession) -> DudiWithAlamat :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.alamat)).where(and_(Dudi.id == id_dudi,Dudi.id_sekolah == id_sekolah)))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,f"Dudi dengan id {id_dudi} tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findDudi
    }
