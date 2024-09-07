from operator import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from sqlalchemy.orm import joinedload

# models
from .siswaManageModel import ResponseSiswaPag
from ...models_domain.siswa_model import MoreSiswa
from ....models.siswaModel import Siswa
# common
from ....error.errorHandling import HttpException
import math

async def getSiswa(id_pembimbing_dudi : int,page : int | None,session : AsyncSession) -> list[MoreSiswa] |  ResponseSiswaPag :
    statementSelectSiswa = select(Siswa).options(joinedload(Siswa.alamat),joinedload(Siswa.kelas),joinedload(Siswa.jurusan),joinedload(Siswa.guru_pembimbing)).where(Siswa.id_pembimbing_dudi == id_pembimbing_dudi)

    if page :
        findSiswa = (await session.execute(statementSelectSiswa.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(Siswa.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findSiswa,
                "count_data" : len(findSiswa),
                "count_page" : countPage
            }
        }
    else :
        findSiswa = (await session.execute(statementSelectSiswa)).scalars().all()
        return {
            "msg" : "success",
            "data" : findSiswa
        }
    
async def getSiswaById(id_pembimbing_dudi : int,id_siswa : int ,session : AsyncSession) -> MoreSiswa :
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.jurusan),joinedload(Siswa.kelas),joinedload(Siswa.guru_pembimbing)).where(and_(Siswa.id_pembimbing_dudi == id_pembimbing_dudi,Siswa.id == id_siswa)))).scalar_one_or_none()

    if not findSiswa :
        print("tes")
        raise HttpException(404,"siswa tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findSiswa
    }