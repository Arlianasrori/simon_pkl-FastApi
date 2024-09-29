import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,case,and_
from sqlalchemy.orm import joinedload

# models
from .getDudiModel import FilterGetDudiQuery,ResponseGetDudiPag
from ....models.dudiModel import Dudi,KuotaSiswa,KuotaSiswaByJurusan
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
    
    # findDudi dan jumlah siswa yang ada pada dudi tersebut
    findDudi = (await session.execute(select(Dudi,siswa_count.c.jumlah_siswa_pria,siswa_count.c.jumlah_siswa_wanita).outerjoin(siswa_count, Dudi.id == siswa_count.c.id_dudi).options(joinedload(Dudi.alamat),joinedload(Dudi.kuota).subqueryload(KuotaSiswa.kuota_jurusan).joinedload(KuotaSiswaByJurusan.jurusan)).where(and_(Dudi.nama_instansi_perusahaan.ilike(f"%{filter.nama_instansi_perusahaan}%") if filter.nama_instansi_perusahaan else True,Dudi.id_sekolah == id_sekolah)).limit(10).offset(10 * (page - 1)))).all()

    # get total dudi yang ada
    countData = (await session.execute(select(func.count(Dudi.id)).where(and_(Dudi.nama_instansi_perusahaan.ilike(f"%{filter.nama_instansi_perusahaan}%") if filter.nama_instansi_perusahaan else True,Dudi.id_sekolah == id_sekolah)))).scalar_one()
    # get total page yang ada 
    countPage = math.ceil(countData / 10)

    responseDudiList = [] # digunakan untuk response ke user tanpa merefresh database setelah commit 
    for dudi in findDudi :
        dudiDecode = dudi._asdict() # decode dudi dengan jumlah_pria dan jumlah_wanita beserta kuotanya

        dudiDictDecode = dudiDecode["Dudi"].__dict__ # decode dudi tanpa jumlah_pria dan jumlah_wanita

        # dudi dictionary yang sesuai dengan format response untuk dikirim ke user
        dudiDict = {
            **dudiDictDecode,
            "jumlah_siswa_pria" : dudiDecode["jumlah_siswa_pria"] if dudiDecode["jumlah_siswa_pria"] else 0,
            "jumlah_siswa_wanita" : dudiDecode["jumlah_siswa_wanita"] if dudiDecode["jumlah_siswa_wanita"] else 0,
            "tersedia" : True
        }

        # cek apakah dudi memiliki kouta atau tidak
        
        if not dudiDecode["Dudi"].kuota :
            dudiDict.update({
            "jumlah_kuota_pria" : 0,
            "jumlah_kuota_wanita" : 0,
            "tersedia" : False
            })
            responseDudiList.append(dudiDict)
            continue
        else :
            dudiDict.update({
            "jumlah_kuota_pria" : dudiDecode["Dudi"].kuota.jumlah_pria if dudiDecode["Dudi"].kuota.jumlah_pria else 0,
            "jumlah_kuota_wanita" : dudiDecode["Dudi"].kuota.jumlah_wanita if dudiDecode["Dudi"].kuota.jumlah_wanita else 0
            })

        # cek apakah dudi sudah penuh
        # apakah jumlah siswa sudah melebihi atau sama dengan total yang ada
        if dudiDict["jumlah_siswa_pria"] + dudiDict["jumlah_siswa_wanita"] >= dudiDictDecode["kuota"].jumlah_pria + dudiDictDecode["kuota"].jumlah_wanita :
            dudiDict["tersedia"] = False
        # cek apakah jumlah siswa pria sudah melebihi atau sama dengan jumlah kuota pria
        elif findSiswa.jenis_kelamin == JenisKelaminEnum.laki and  dudiDictDecode["kuota"].jumlah_pria != 0:
            if dudiDict["jumlah_siswa_pria"] + 1 > dudiDictDecode["kuota"].jumlah_pria :
                dudiDict["tersedia"] = False
        # cek apakah jumlah siswa wanita sudah melebihi atau sama dengan jumlah kuota wanita
        elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and  dudi["kuota"].jumlah_wanita != 0:
            if dudiDict["jumlah_siswa_wanita"] + 1 > dudi["kuota"].jumlah_wanita :
                dudiDict["tersedia"] = False

        kuotaJurusanList = [] # untuk kuotanjurusan response untuk dikirim ke user
        totalKebutuhanLaki = 0 # untuk total kebutuhan laki
        totalKebutuhanWanita = 0 # untuk total kebutuhan wanita
        totalSiswaLakiAlljurusan = 0 # untuk total siswa laki semua jurusan
        totalSiswaWanitaAlljurusan = 0 # untuk total siswa wanita semua jurusan
        lolosSeleksiJurusan = False # digunakan sebagai penanda apakah siswa lolol dalam seleksi jurusan atau tidak

        for kuota_jurusan in dudiDictDecode["kuota"].kuota_jurusan :     
            # get total siswa laki dan wanita pada dudi berdasarkan kuota jurusan
            countDudiBykuota = (await session.execute(select(
                func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.laki).label("jumlah_siswa_pria"),
                func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.perempuan).label("jumlah_siswa_wanita"),
            ).where(
                and_(
                    Siswa.id_jurusan == kuota_jurusan.id_jurusan,
                    Siswa.id_dudi == dudiDict["id"]
                )
            ))).one()._asdict()

            # validasi jika count siswa by jurusa mereturn None
            countDudiBykuota["jumlah_siswa_pria"] = countDudiBykuota["jumlah_siswa_pria"] if countDudiBykuota["jumlah_siswa_pria"] else 0
            countDudiBykuota["jumlah_siswa_wanita"] = countDudiBykuota["jumlah_siswa_wanita"] if countDudiBykuota["jumlah_siswa_wanita"] else 0

            # menambahkan total kebutuhan laki dan wanita
            totalKebutuhanLaki += kuota_jurusan.jumlah_pria
            totalKebutuhanWanita += kuota_jurusan.jumlah_wanita
            totalSiswaLakiAlljurusan += countDudiBykuota["jumlah_siswa_pria"]
            totalSiswaWanitaAlljurusan += countDudiBykuota["jumlah_siswa_wanita"]
            
            # jika siswa memiliki jurusan yang sama dengan kuota jurusan
            if kuota_jurusan.id_jurusan == findSiswa.jurusan.id :  
                if findSiswa.jenis_kelamin == JenisKelaminEnum.laki and kuota_jurusan.jumlah_pria != 0:
                    # cek apakah jumlah siswa pria akan melebihi kuota jurusan jika ditambah dengan user
                    if countDudiBykuota["jumlah_siswa_pria"] + 1 > kuota_jurusan.jumlah_pria :
                        dudiDict["tersedia"] = False
                    else :
                        lolosSeleksiJurusan = True
                elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan and kuota_jurusan.jumlah_wanita != 0:
                    # cek apakah jumlah siswa wanita akan melebihi kuota jurusan jika ditambah dengan user
                    if countDudiBykuota["jumlah_siswa_wanita"] + 1 > kuota_jurusan.jumlah_wanita :
                        dudiDict["tersedia"] = False
                    else :
                        lolosSeleksiJurusan = True
            
            # maping kuota jurusan for response later
            kuotaJurusanMapping = {
                "jurusan" : kuota_jurusan.jurusan.nama,
                "kuota_pria" : kuota_jurusan.jumlah_pria,
                "kuota_wanita" : kuota_jurusan.jumlah_wanita,
                "jumlah_siswa_pria" : countDudiBykuota["jumlah_siswa_pria"] if countDudiBykuota["jumlah_siswa_pria"] else 0,
                "jumlah_siswa_wanita" : countDudiBykuota["jumlah_siswa_wanita"] if countDudiBykuota["jumlah_siswa_wanita"] else 0
            }

            # append kuota jurusan ke list
            kuotaJurusanList.append(kuotaJurusanMapping)

        # hitung kebutuhan kuota disemua jurusan : semua kuota jurusan,kuotanya ditambahkan dan dikurangi dengan totalSiswa disemua jurusan.Didapatkan sisa berapa kuota dijurusan yang belum terpenuhi
        kebutuhanJurusanLaki = totalKebutuhanLaki - totalSiswaLakiAlljurusan
        kebutuhanJurusanWanita = totalKebutuhanWanita - totalSiswaWanitaAlljurusan
        # hitung tinggal berapa kuota yang tersisah didudi saat ini : kuota yang ada dikurangi dengan jumlah siswa didudi.Didapatkan tinggal berapa siswa kuota untuk dudi yang ada
        sisakuotaDudiPria = dudiDecode["Dudi"].kuota.jumlah_pria - dudiDict["jumlah_siswa_pria"]
        sisakuotaDudiWanita = dudiDecode["Dudi"].kuota.jumlah_wanita - dudiDict["jumlah_siswa_wanita"]

        # jika siswa tidak lolos jurusan lanjut validasi untuk kouta umum
        if not lolosSeleksiJurusan :
            if findSiswa.jenis_kelamin == JenisKelaminEnum.laki :
                # cek apakah sisa kuota pada dudi lebih kecil atau sama dengan jumlah kuota yang belum terpenuhi disemua jurusan.Maksudnya apakah sisa kuota pada dudi masih bisa menampung total kuota yang ada pada jurusan.jika tidak bisa maka user dengan jurusan selain itu tidak diizinkan
                if sisakuotaDudiPria <= kebutuhanJurusanLaki :
                    dudiDict["tersedia"] = False
            elif findSiswa.jenis_kelamin == JenisKelaminEnum.perempuan :
                # cek apakah sisa kuota pada dudi lebih kecil atau sama dengan jumlah kuota yang belum terpenuhi disemua jurusan.Maksudnya apakah sisa kuota pada dudi masih bisa menampung total kuota yang ada pada jurusan.jika tidak bisa maka user dengan jurusan selain itu tidak diizinkan
                if sisakuotaDudiWanita <= kebutuhanJurusanWanita :
                    dudiDict["tersedia"] = False

        dudiDict["kuota_jurusan"] = kuotaJurusanList
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