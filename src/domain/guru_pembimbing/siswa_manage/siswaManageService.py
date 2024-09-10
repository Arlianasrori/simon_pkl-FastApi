from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_,func
from sqlalchemy.orm import joinedload

# models
from ....models.siswaModel import Siswa
from ...models_domain.siswa_model import SiswaWithDudi,DetailSiswa
from .siswaManageModel import ResponseSiswaPag

# common 
from ....error.errorHandling import HttpException
import math


async def getAllSiswa(id_guru : int,id_sekolah : int,page : int | None,session : AsyncSession) -> list[SiswaWithDudi] | ResponseSiswaPag :
    """
    Get all students from the database.

    Args:
        id_guru (int): The ID of the teacher.
        id_sekolah (int): The ID of the school.
        session (AsyncSession): The database session.
    """
    statementSelectSiswa = select(Siswa).where(and_(Siswa.id_sekolah == id_sekolah,Siswa.id_guru_pembimbing == id_guru))
    
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

async def getSiswaById(id_siswa : int,id_guru : int,session : AsyncSession) -> DetailSiswa :
    findSiswa = (await session.execute(select(Siswa).options(joinedload(Siswa.alamat),joinedload(Siswa.jurusan),joinedload(Siswa.kelas),joinedload(Siswa.dudi),joinedload(Siswa.pembimbing_dudi),joinedload(Siswa.guru_pembimbing)).where(and_(Siswa.id == id_siswa,Siswa.id_guru_pembimbing == id_guru)))).scalar_one_or_none()

    if not findSiswa :
        raise HttpException(400,f"Siswa dengan id {id_siswa} tidak ditemukan")
    return {
        "msg" : "success",
        "data" : findSiswa
    }
    

