from operator import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import joinedload,subqueryload

# models
from .koutaDudiModel import AddKoutaDudiBody,UpdateKoutaDudiBody
from ....models.dudiModel import Dudi, KoutaSiswa
from ...models_domain.dudi_model import DudiWithKouta
# common
from copy import deepcopy
from ....error.errorHandling import HttpException
from ....utils.updateTable import updateTable


async def getKoutaDudi(id_dudi : int,session : AsyncSession) -> DudiWithKouta :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findDudi
    }
async def addKoutaDudi(id_dudi : int,kouta : AddKoutaDudiBody,session : AsyncSession) -> DudiWithKouta:
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    if findDudi.kouta :
        raise HttpException(400,"Kouta siswa sudah ditambahkan")
    
    koutaMapping = kouta.model_dump()
    koutaMapping.update({"id_dudi" : id_dudi})
    session.add(KoutaSiswa(**koutaMapping))
    findDudi.tersedia = True;
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : {
            **dudiDictCopy,
            "kouta" : koutaMapping
        }
    }

async def updateKoutaDudi(id_dudi : int,kouta : UpdateKoutaDudiBody,session : AsyncSession) -> DudiWithKouta :
    findDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.kouta),subqueryload(Dudi.siswa)).where(Dudi.id == id_dudi))).scalar_one_or_none()

    if not findDudi :
        raise HttpException(404,"Dudi tidak ditemukan")
    
    if not findDudi.kouta :
        raise HttpException(404,"Kouta siswa belum ditambahkan")
    
    
    if kouta.jumlah_pria < len(findDudi.siswa) :
        raise HttpException(400,"kouta pria tidak boleh kurang dari jumlah siswa")
    
    if kouta.jumlah_wanita < len(findDudi.siswa) :
        raise HttpException(400,"kouta wanita tidak boleh kurang dari jumlah siswa")
    
    if kouta != {} :
        updateTable(kouta,findDudi.kouta)
    
    dudiDictCopy = deepcopy(findDudi.__dict__)
    await session.commit()
    
    return {
        "msg" : "success",
        "data" : dudiDictCopy
    }
    