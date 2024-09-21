from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.dudiModel import Dudi
from ....models.siswaModel import Siswa
from ...models_domain.dudi_model import DudiWithAlamat

# common
from ....error.errorHandling import HttpException

async def getDudiByGuru(id_guru : int,session : AsyncSession) -> list[DudiWithAlamat] :
    getSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.dudi)).where(Siswa.id_guru_pembimbing == id_guru))).scalars().all()

    unique_id_dudi = set(siswa.id_dudi for siswa in getSiswa if siswa.id_dudi is not None)
    getDudi = (await session.execute(select(Dudi).options(joinedload(Dudi.alamat)).where(Dudi.id.in_(unique_id_dudi)))).scalars().all()
    return {
        "msg" : "success",
        "data" : getDudi
    }