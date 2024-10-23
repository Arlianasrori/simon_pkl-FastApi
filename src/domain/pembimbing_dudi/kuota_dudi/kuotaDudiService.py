from operator import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import joinedload,subqueryload

# models
from ....models.types import JenisKelaminEnum
from .kuotaDudiModel import AddKuotaDudiBody,UpdateKuotaDudiBody,AddKuotaJurusanBody
from ....models.dudiModel import Dudi, KuotaSiswa,KuotaSiswaByJurusan
from ...models_domain.dudi_model import DudiWithKuota
from ....models.siswaModel import Jurusan
from ....models.siswaModel import Siswa,Jurusan
# common
from copy import deepcopy
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable
from python_random_strings import random_strings

async def getKuotaDudi(id_dudi : int,session : AsyncSession) -> DudiWithKuota :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kuota).subqueryload(KuotaSiswa.kuota_jurusan).joinedload(KuotaSiswaByJurusan.jurusan)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findDudi
    }
async def addKuotaDudi(id_dudi : int,kuota : AddKuotaDudiBody,session : AsyncSession) -> DudiWithKuota:
    print(kuota)
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kuota)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    if findDudi.kuota :
        raise HttpException(400,"Kuota siswa sudah ditambahkan")
    
    kuotaMapping = kuota.model_dump(exclude={"kuota_jurusan"})
    kuotaMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi})

    jurusanTotalPria = 0
    jurusanTotalWanita = 0
    jurusanMappingList = []
    jurusanForResponse = []

    if kuota.kuota_jurusan :
        for kuotaJurusan in kuota.kuota_jurusan :          
            findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == kuotaJurusan.id_jurusan))).scalar_one_or_none()

            if not findJurusan :
                raise HttpException(404,"Jurusan tidak ditemukan")
            
            kuotaJurusanMapping = kuotaJurusan.model_dump()
            # mapping kuota andd add id kuota 
            kuotaJurusanMapping.update({"id" : random_strings.random_digits(6),"id_kuota" : kuotaMapping["id"]})
            jurusanMappingList.append(KuotaSiswaByJurusan(**kuotaJurusanMapping))

            # add jurusan on mapping for response
            kuotaJurusanMapping.update({"jurusan" : deepcopy(findJurusan.__dict__)})
            jurusanForResponse.append(kuotaJurusanMapping)

            jurusanTotalPria += kuotaJurusanMapping["jumlah_pria"]
            jurusanTotalWanita += kuotaJurusanMapping["jumlah_wanita"]

    if jurusanTotalPria > kuota.jumlah_pria :
        raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi kuota")    
    if jurusanTotalWanita > kuota.jumlah_wanita :
        raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi kuota")
    
    print(kuotaMapping)
    session.add(KuotaSiswa(**kuotaMapping))
    session.add_all(jurusanMappingList)
    findDudi.tersedia = True;

    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    print(jurusanForResponse)
    
    return {
        "msg" : "success",
        "data" : {
            **dudiDictCopy,
            "kuota" : {
                **kuotaMapping,
                "kuota_jurusan" : jurusanForResponse
            }
        }
    }

async def updateKuotaDudi(id_dudi : int,kuota : UpdateKuotaDudiBody,session : AsyncSession) -> DudiWithKuota :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kuota).subqueryload(KuotaSiswa.kuota_jurusan).joinedload(KuotaSiswaByJurusan.jurusan),subqueryload(Dudi.siswa)).where(Dudi.id == id_dudi))).scalar_one_or_none()
    
    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")

    countSiswa = (await session.execute(select(func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.laki.value).label("count_pria"),func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.perempuan.value).label("count_wanita")).where(Siswa.id_dudi == id_dudi))).one()._asdict()
    countSiswa["count_pria"] = countSiswa["count_pria"] if countSiswa["count_pria"] else 0
    countSiswa["count_wanita"] = countSiswa["count_wanita"] if countSiswa["count_wanita"] else 0

    
    jurusanTotalPria = 0
    jurusanTotalWanita = 0
    jurusanResponseList = []
    
    print(kuota.kuota_jurusan)
    if kuota.kuota_jurusan :
        for kuotaJurusan in kuota.kuota_jurusan :
            print("ngentot")
            print(kuotaJurusan.id)
            findKuotaJurusan = (await session.execute(select(KuotaSiswaByJurusan).where(KuotaSiswaByJurusan.id == kuotaJurusan.id))).scalar_one_or_none()

            if not findKuotaJurusan :
                raise HttpException(404,"Kuota jurusan tidak ditemukan")

            # add to response dict
            updateTable(kuotaJurusan,findKuotaJurusan)
            jurusanResponseList.append(deepcopy(findKuotaJurusan.__dict__))

        for kuotaJurusanDudi in findDudi.kuota.kuota_jurusan :
            for kuotaJurusanFromBody in kuota.kuota_jurusan :
                if kuotaJurusanDudi.id == kuotaJurusanFromBody.id :
                    if kuotaJurusanFromBody.jumlah_pria :
                        jurusanTotalPria += kuotaJurusanFromBody.jumlah_pria
                    if kuotaJurusanFromBody.jumlah_wanita :
                        jurusanTotalWanita += kuotaJurusanFromBody.jumlah_wanita
                else :
                    jurusanTotalPria += kuotaJurusanDudi.jumlah_pria
                    jurusanTotalWanita += kuotaJurusanDudi.jumlah_wanita
            

    # cek apakah kuota pada jurusan tidak melebihi jumlah total kuota
    # cek for pria
    if kuota.jumlah_pria :
        print(jurusanTotalPria)
        print(kuota.jumlah_pria)
        if jurusanTotalPria > kuota.jumlah_pria :
            raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi total kuota") 
    else :
        print("masuk kerpia else")
        if jurusanTotalPria > findDudi.kuota.jumlah_pria :
            raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi total kuota") 

    # cek for wanita   
    if kuota.jumlah_wanita :
        print("masuk wanita if")
        if jurusanTotalWanita > kuota.jumlah_wanita :
            raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi total kuota") 
    else :
        print("masuk wanita else")
        if jurusanTotalWanita > findDudi.kuota.jumlah_wanita :
            raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi total kuota") 
    
    # cek apakah jumlah total kouts tidak kurang dari jumlah siswa yang telah ada
    if kuota.jumlah_pria and kuota.jumlah_pria < countSiswa["count_pria"] :
        raise HttpException(400,"kuota pria yang anda berikan kurang dari jumlah siswa pria yang ada pada dudi saat ini")
    if kuota.jumlah_wanita and kuota.jumlah_wanita < countSiswa["count_wanita"] :
        raise HttpException(400,"kuota wanita yang anda berikan kurang dari jumlah siswa wanita yang ada pada dudi saat ini")

    if kuota.model_dump(exclude={"kuota_jurusan"}) != {} :
        updateTable(kuota.model_dump(exclude={"kuota_jurusan"}),findDudi.kuota)
    
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : {
            **dudiDictCopy,
            "kuota" : {
                **dudiDictCopy["kuota"].__dict__,
                "kuota_jurusan" : jurusanResponseList
            }
        }
    }

async def addKuotaJurusan(id_dudi : int,kuota : list[AddKuotaJurusanBody],session : AsyncSession) -> DudiWithKuota :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kuota).subqueryload(KuotaSiswa.kuota_jurusan).joinedload(KuotaSiswaByJurusan.jurusan)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    if not findDudi.kuota :
        raise HttpException(404,"Kuota siswa belum ditambahkan")
        
    countMaxSiswa = (await session.execute(select(func.sum(KuotaSiswaByJurusan.jumlah_pria).label("count_pria"),func.sum(KuotaSiswaByJurusan.jumlah_wanita).label("count_wanita")).where(KuotaSiswaByJurusan.id_kuota == findDudi.kuota.id))).one()._asdict()

    countMaxSiswaDict = {
        "count_pria" : countMaxSiswa["count_pria"] if countMaxSiswa["count_pria"] else 0,
        "count_wanita" : countMaxSiswa["count_wanita"] if countMaxSiswa["count_wanita"] else 0,
    }
    listkuotaForDb = []
    listkuotaForResponse = []
    
    if len(kuota) > 0 :
        for kuotaJurusan in kuota :
            findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == kuotaJurusan.id_jurusan))).scalar_one_or_none()

            if not findJurusan :
                raise HttpException(404,"Jurusan tidak ditemukan")
            
            findKuotaJurusan = (await session.execute(select(KuotaSiswaByJurusan).where(KuotaSiswaByJurusan.id_jurusan == kuotaJurusan.id_jurusan))).scalar_one_or_none()

            if findKuotaJurusan :
                raise HttpException(404,"Kuota untuk jurusan ini telah ditambahkan")
            
            # mapping kuota and add id and id_kuota
            kuotaJurusanMapping = kuotaJurusan.model_dump()
            kuotaJurusanMapping.update({"id" : random_strings.random_digits(6),"id_kuota" : findDudi.kuota.id})

            # add to list for db,to add all later
            listkuotaForDb.append(KuotaSiswaByJurusan(**kuotaJurusanMapping))

            # add to list for response
            listkuotaForResponse.append({
                **kuotaJurusanMapping,
                "jurusan" : deepcopy(findJurusan.__dict__)
            })

            # increment count max siswa
            countMaxSiswaDict["count_pria"] += kuotaJurusanMapping["jumlah_pria"]
            countMaxSiswaDict["count_wanita"] += kuotaJurusanMapping["jumlah_wanita"]
    else :
        raise HttpException(400,"kuota jurusan tidak boleh kosong")
    
    # check if jika total kuota melebihi maximal kuota yang telah ditentukan
    if countMaxSiswaDict["count_pria"] > findDudi.kuota.jumlah_pria :
        raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi total kuota") 
    if countMaxSiswaDict["count_wanita"] > findDudi.kuota.jumlah_wanita :
        raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi total kuota") 

    session.add_all(listkuotaForDb)
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : {
            **dudiDictCopy,
            "kuota" : {
                **dudiDictCopy["kuota"].__dict__,
                "kuota_jurusan" : listkuotaForResponse
            }
        }
    }
