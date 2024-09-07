from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

# models]
from ...models_domain.pembimbing_dudi_model import PembimbingDudiBase,PembimbingDudiWithAlamatDudi
from ....models.pembimbingDudiModel import PembimbingDudi

# common
from ....error.errorHandling import HttpException

async def getPembimbingDudi(id_pembimbing_dudi : int,session : AsyncSession) -> PembimbingDudiBase :
    print(id_pembimbing_dudi)
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id == id_pembimbing_dudi))).scalar_one_or_none()

    if not findPembimbingDudi :
        raise HttpException(404,"pembimbing dudi tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPembimbingDudi
    }

async def getProfile(id_pembimbing_dudi : int,session : AsyncSession) -> PembimbingDudiWithAlamatDudi :
    findPembimbingDudi = (await session.execute(select(PembimbingDudi).options(joinedload(PembimbingDudi.alamat),joinedload(PembimbingDudi.dudi)).where(PembimbingDudi.id == id_pembimbing_dudi))).scalar_one_or_none()

    if not findPembimbingDudi :
        raise HttpException(404,"pembimbing dudi tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findPembimbingDudi
    }