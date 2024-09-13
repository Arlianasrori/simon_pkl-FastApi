from operator import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import joinedload,subqueryload

# models
from .koutaDudiModel import AddKoutaDudiBody,UpdateKoutaDudiBody
from ....models.dudiModel import Dudi, KoutaSiswa,KoutaSiswaByJurusan
from ...models_domain.dudi_model import DudiWithKouta
from ....models.siswaModel import Jurusan
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

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    if not findDudi.kouta :
        raise HttpException(404,"Kouta siswa belum ditambahkan")
    
    jurusanTotalPria = 0
    jurusanTotalWanita = 0
    jurusanResponseList = []

    if kouta.kouta_jurusan :
        for koutaJurusan in kouta.kouta_jurusan :  
            findKoutaJurusan = (await session.execute(select(KoutaSiswaByJurusan).where(KoutaSiswaByJurusan.id == koutaJurusan.id))).scalar_one_or_none()

            if not findKoutaJurusan :
                if not koutaJurusan.id_jurusan :
                    raise HttpException(400,"kouta jurusan yang ditambahkan tidak ditemukan,harap tambahkan jurusan untuk menambahkan kouta")
                
                findJurusan = (await session.execute(select(Jurusan).where(Jurusan.id == koutaJurusan.id_jurusan))).scalar_one_or_none()

                if not findJurusan :
                    raise HttpException(404,"Jurusan tidak ditemukan")
                
                findJurusanByKouta = (await session.execute(select(KoutaSiswaByJurusan).where(and_(KoutaSiswaByJurusan.id_kouta == findDudi.kouta.id,KoutaSiswaByJurusan.id_jurusan == koutaJurusan.id_jurusan)))).scalar_one_or_none()

                if findJurusanByKouta :
                    raise HttpException(400,"kouta dengan jurusan ini sudah ditambahkan")

                jurusanMapping = koutaJurusan.model_dump()
                jurusanMapping.update({"id" : random_strings.random_digits(6),"id_kouta" : findDudi.kouta.id})
                print(jurusanMapping)
                session.add(KoutaSiswaByJurusan(**jurusanMapping))
                jurusanMapping.update({"jurusan" : deepcopy(findJurusan.__dict__)})

                # add to response dict
                jurusanResponseList.append(jurusanMapping)
            else :
                # add to response dict
                jurusanResponseList.append(deepcopy(findKoutaJurusan.__dict__))
                updateTable(koutaJurusan,findKoutaJurusan)
            

            jurusanTotalPria += koutaJurusan.jumlah_pria
            jurusanTotalWanita += koutaJurusan.jumlah_wanita
            

    # cek apakah kouta pada jurusan tidak melebihi jumlah total kouta
    if jurusanTotalPria > kouta.jumlah_pria :
        raise HttpException(400,"Jumlah pria yang ditentukan pada masing - masing jurusan melebihi kouta")    
    if jurusanTotalWanita > kouta.jumlah_wanita :
        raise HttpException(400,"Jumlah wanita yang ditentukan pada masing - masing jurusan melebihi kouta")
    
    # cek apakah jumlah total kouts tidak kurang dari jumlah siswa yang telah ada
    if kouta.jumlah_pria < len(findDudi.siswa) :
        raise HttpException(400,"kouta pria tidak boleh kurang dari jumlah siswa")
    
    if kouta.jumlah_wanita < len(findDudi.siswa) :
        raise HttpException(400,"kouta wanita tidak boleh kurang dari jumlah siswa")
    
    print(kouta)
    print(findDudi.kouta)
    if kouta != {} :
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
    