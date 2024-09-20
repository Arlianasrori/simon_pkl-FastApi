from operator import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import joinedload,subqueryload

# models
from ....models.types import JenisKelaminEnum
from .koutaDudiModel import AddKoutaDudiBody,UpdateKoutaDudiBody,AddKoutaJurusanBody
from ....models.dudiModel import Dudi, KoutaSiswa,KoutaSiswaByJurusan
from ...models_domain.dudi_model import DudiWithKouta
from ....models.siswaModel import Jurusan
from ....models.siswaModel import Siswa
# common
from copy import deepcopy
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable
from python_random_strings import random_strings


async def getKoutaDudi(id_dudi : int,session : AsyncSession) -> DudiWithKouta :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta).subqueryload(KoutaSiswa.kouta_jurusan).joinedload(KoutaSiswaByJurusan.jurusan)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findDudi
    }
async def addKoutaDudi(id_dudi : int,kouta : AddKoutaDudiBody,session : AsyncSession) -> DudiWithKouta:
    print(kouta)
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    if findDudi.kouta :
        raise HttpException(400,"Kouta siswa sudah ditambahkan")
    
    koutaMapping = kouta.model_dump(exclude={"kouta_jurusan"})
    koutaMapping.update({"id" : random_strings.random_digits(6),"id_dudi" : id_dudi})

    jurusanTotalPria = 0
    jurusanTotalWanita = 0
    jurusanMappingList = []
    jurusanForResponse = []

    if kouta.kouta_jurusan :
        for koutaJurusan in kouta.kouta_jurusan :          
            findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == koutaJurusan.id_jurusan))).scalar_one_or_none()

            if not findJurusan :
                raise HttpException(404,"Jurusan tidak ditemukan")
            
            koutaJurusanMapping = koutaJurusan.model_dump()
            # mapping kouta andd add id kouta 
            koutaJurusanMapping.update({"id" : random_strings.random_digits(6),"id_kouta" : koutaMapping["id"]})
            jurusanMappingList.append(KoutaSiswaByJurusan(**koutaJurusanMapping))

            # add jurusan on mapping for response
            koutaJurusanMapping.update({"jurusan" : deepcopy(findJurusan.__dict__)})
            jurusanForResponse.append(koutaJurusanMapping)

            jurusanTotalPria += koutaJurusanMapping["jumlah_pria"]
            jurusanTotalWanita += koutaJurusanMapping["jumlah_wanita"]

    if jurusanTotalPria > kouta.jumlah_pria :
        raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi kouta")    
    if jurusanTotalWanita > kouta.jumlah_wanita :
        raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi kouta")
    
    print(koutaMapping)
    session.add(KoutaSiswa(**koutaMapping))
    session.add_all(jurusanMappingList)
    findDudi.tersedia = True;

    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    print(jurusanForResponse)
    
    return {
        "msg" : "success",
        "data" : {
            **dudiDictCopy,
            "kouta" : {
                **koutaMapping,
                "kouta_jurusan" : jurusanForResponse
            }
        }
    }

async def updateKoutaDudi(id_dudi : int,kouta : UpdateKoutaDudiBody,session : AsyncSession) -> DudiWithKouta :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta).subqueryload(KoutaSiswa.kouta_jurusan).joinedload(KoutaSiswaByJurusan.jurusan),subqueryload(Dudi.siswa)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    countSiswa = (await session.execute(select(func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.laki.value).label("count_pria"),func.count(Siswa.id).filter(Siswa.jenis_kelamin == JenisKelaminEnum.perempuan.value).label("count_wanita")).where(Siswa.id_dudi == id_dudi))).one()._asdict()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    jurusanTotalPria = 0
    jurusanTotalWanita = 0
    jurusanResponseList = []

    if kouta.kouta_jurusan :
        for koutaJurusan in kouta.kouta_jurusan :  
            findKoutaJurusan = (await session.execute(select(KoutaSiswaByJurusan).where(KoutaSiswaByJurusan.id == koutaJurusan.id))).scalar_one_or_none()

            if not findKoutaJurusan :
                raise HttpException(404,"Kouta jurusan tidak ditemukan")

            # add to response dict
            updateTable(koutaJurusan,findKoutaJurusan)
            jurusanResponseList.append(deepcopy(findKoutaJurusan.__dict__))

        for koutaJurusanDudi in findDudi.kouta.kouta_jurusan :
            for koutaJurusanFromBody in kouta.kouta_jurusan :
                if koutaJurusanDudi.id == koutaJurusanFromBody.id :
                    if koutaJurusanFromBody.jumlah_pria :
                        jurusanTotalPria += koutaJurusanFromBody.jumlah_pria
                    if koutaJurusanFromBody.jumlah_wanita :
                        jurusanTotalWanita += koutaJurusanFromBody.jumlah_wanita
                else :
                    jurusanTotalPria += koutaJurusanDudi.jumlah_pria
                    jurusanTotalWanita += koutaJurusanDudi.jumlah_wanita
            

    # cek apakah kouta pada jurusan tidak melebihi jumlah total kouta
    # cek for pria
    if kouta.jumlah_pria :
        print("masuk kerpia if")
        if jurusanTotalPria > kouta.jumlah_pria :
            raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi total kouta") 
    else :
        print("masuk kerpia else")
        if jurusanTotalPria > findDudi.kouta.jumlah_pria :
            raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi total kouta") 

    # cek for wanita   
    if kouta.jumlah_wanita :
        print("masuk wanita if")
        if jurusanTotalWanita > kouta.jumlah_wanita :
            raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi total kouta") 
    else :
        print("masuk wanita else")
        if jurusanTotalWanita > findDudi.kouta.jumlah_wanita :
            raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi total kouta") 
    
    # cek apakah jumlah total kouts tidak kurang dari jumlah siswa yang telah ada
    if kouta.jumlah_pria and kouta.jumlah_pria < countSiswa["count_pria"] :
        raise HttpException(400,"kouta pria yang anda berikan kurang dari jumlah siswa pria yang ada pada dudi saat ini")
    if kouta.jumlah_wanita and kouta.jumlah_wanita < countSiswa["count_wanita"] :
        raise HttpException(400,"kouta wanita yang anda berikan kurang dari jumlah siswa wanita yang ada pada dudi saat ini")

    if kouta.model_dump(exclude={"kouta_jurusan"}) != {} :
        updateTable(kouta.model_dump(exclude={"kouta_jurusan"}),findDudi.kouta)
    
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : {
            **dudiDictCopy,
            "kouta" : {
                **dudiDictCopy["kouta"].__dict__,
                "kouta_jurusan" : jurusanResponseList
            }
        }
    }

async def addKoutaJurusan(id_dudi : int,kouta : list[AddKoutaJurusanBody],session : AsyncSession) -> DudiWithKouta :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta).subqueryload(KoutaSiswa.kouta_jurusan).joinedload(KoutaSiswaByJurusan.jurusan)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    if not findDudi.kouta :
        raise HttpException(404,"Kouta siswa belum ditambahkan")
        
    countMaxSiswa = (await session.execute(select(func.sum(KoutaSiswaByJurusan.jumlah_pria).label("count_pria"),func.sum(KoutaSiswaByJurusan.jumlah_wanita).label("count_wanita")).where(KoutaSiswaByJurusan.id_kouta == findDudi.kouta.id))).one()._asdict()

    listkoutaForDb = []
    listkoutaForResponse = []
    
    if len(kouta) > 0 :
        for koutaJurusan in kouta :
            findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == koutaJurusan.id_jurusan))).scalar_one_or_none()

            if not findJurusan :
                raise HttpException(404,"Jurusan tidak ditemukan")
            
            findKoutaJurusan = (await session.execute(select(KoutaSiswaByJurusan).where(KoutaSiswaByJurusan.id_jurusan == koutaJurusan.id_jurusan))).scalar_one_or_none()

            if findKoutaJurusan :
                raise HttpException(404,"Kouta untuk jurusan ini telah ditambahkan")
            
            # mapping kouta and add id and id_kouta
            koutaJurusanMapping = koutaJurusan.model_dump()
            koutaJurusanMapping.update({"id" : random_strings.random_digits(6),"id_kouta" : findDudi.kouta.id})

            # add to list for db,to add all later
            listkoutaForDb.append(KoutaSiswaByJurusan(**koutaJurusanMapping))

            # add to list for response
            listkoutaForResponse.append({
                **koutaJurusanMapping,
                "jurusan" : deepcopy(findJurusan.__dict__)
            })

            # increment count max siswa
            countMaxSiswa["count_pria"] += koutaJurusanMapping["jumlah_pria"]
            countMaxSiswa["count_wanita"] += koutaJurusanMapping["jumlah_wanita"]
    else :
        raise HttpException(400,"kouta jurusan tidak boleh kosong")
    
    # check if jika total kouta melebihi maximal kouta yang telah ditentukan
    if countMaxSiswa["count_pria"] > findDudi.kouta.jumlah_pria :
        raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi total kouta") 
    if countMaxSiswa["count_wanita"] > findDudi.kouta.jumlah_wanita :
        raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi total kouta") 

    session.add_all(listkoutaForDb)
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : {
            **dudiDictCopy,
            "kouta" : {
                **dudiDictCopy["kouta"].__dict__,
                "kouta_jurusan" : listkoutaForResponse
            }
        }
    }
