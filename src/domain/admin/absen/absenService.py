from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from sqlalchemy.orm import joinedload

# models
from .absenModel import FilterAbsenQuery
from ...models_domain.absen_model import MoreAbsen, SiswaWithAbsen
from ....models.absenModel import Absen
from ....models.siswaModel import Siswa

# common 
import math
from ....error.errorHandling import HttpException
import datetime

async def getAllAbsen(page: int, id_sekolah: int, id_tahun: int, query: FilterAbsenQuery | None, session: AsyncSession) -> SiswaWithAbsen:
    """
    Retrieve all attendance records with pagination and filtering options.

    Args:
        page (int): The page number for pagination.
        id_sekolah (int): The school ID.
        id_tahun (int): The year ID.
        query (FilterAbsenQuery | None): Query parameters for filtering.
        session (AsyncSession): The database session.

    Returns:
        SiswaWithAbsen: A dictionary containing the retrieved attendance data and pagination information.
    """
    if (not query.tanggal) and (query.month or query.year):
        now = datetime.datetime.now()
        startQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 1, 1)
        endQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 12, 31)

    getSiswaWithAbsen = (await session.execute(select(Siswa).options(joinedload(Siswa.absen.and_(and_((Absen.tanggal >= startQuery, Absen.tanggal <= endQuery) if query.month or query.year else True, Absen.tanggal == query.tanggal if query.tanggal else True, Absen.id_siswa == query.id_siswa if query.id_siswa else True, Absen.status == query.status if query.status else True)))).limit(10).offset(10 * (page - 1)).where(and_(Siswa.id_sekolah == id_sekolah, Siswa.id_tahun == id_tahun)))).scalars().all()

    conntData = (await session.execute(func.count(Siswa.id))).scalar_one()
    countPage = math.ceil(conntData / 10)

    return {
        "msg": "success",
        "data": {
            "data": getSiswaWithAbsen,
            "count_data": len(getSiswaWithAbsen),
            "count_page": countPage
        }
    }

async def getAbsenById(id_absen: int, id_sekolah, session: AsyncSession) -> MoreAbsen:
    """
    Retrieve a specific attendance record by its ID.

    Args:
        id_absen (int): The ID of the attendance record.
        id_sekolah: The school ID.
        session (AsyncSession): The database session.

    Returns:
        MoreAbsen: A dictionary containing the retrieved attendance data.

    Raises:
        HttpException: If the attendance record is not found.
    """
    findAbsen = (await session.execute(select(Absen).options(joinedload(Absen.siswa), joinedload(Absen.keterangan_absen_masuk), joinedload(Absen.keterangan_absen_pulang)).where(and_(Absen.id == id_absen, Absen.siswa.has(Siswa.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findAbsen:
        raise HttpException(404, "absen tidak ditemukan")
    
    return {
        "msg": "success",
        "data": findAbsen
    }