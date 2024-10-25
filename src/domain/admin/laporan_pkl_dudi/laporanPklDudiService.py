from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from sqlalchemy.orm import joinedload

# models
from .laporanPklDudiModel import ResponseLaporanPklDudiPag, FilterLaporanPklDudiQuery
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from ....models.laporanPklModel import LaporanPKL
from ....models.sekolahModel import TahunSekolah
from ....models.siswaModel import Siswa
from ....models.dudiModel import Dudi

# common 
import math
import datetime
from ....error.errorHandling import HttpException

async def getAllLaporanPkl(page: int, id_sekolah: int, id_tahun: int, query: FilterLaporanPklDudiQuery | None, session: AsyncSession) -> ResponseLaporanPklDudiPag:
    """
    Retrieve all PKL reports based on given parameters.

    Args:
        page (int): The page number for pagination.
        id_sekolah (int): The school ID.
        id_tahun (int): The year ID.
        query (FilterLaporanPklDudiQuery | None): Query parameters for filtering.
        session (AsyncSession): The database session.

    Returns:
        ResponseLaporanPklDudiPag: A dictionary containing the retrieved PKL reports and pagination information.

    Raises:
        HttpException: If the specified year is not found.
    """
    
    if query.month or query.year:
        now = datetime.datetime.now()
        startQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 1, 1)
        endQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 12, 31)
        print(startQuery)

    statement = select(LaporanPKL).options(joinedload(LaporanPKL.dudi), joinedload(LaporanPKL.pembimbing_dudi)).where(and_(and_(LaporanPKL.tanggal >= startQuery, LaporanPKL.tanggal <= endQuery)) if query.month else True, LaporanPKL.tanggal == query.tanggal if query.tanggal else True, LaporanPKL.dudi.has(Dudi.id_sekolah == id_sekolah)).limit(10).offset(10 * (page - 1))

    getLapoaran = (await session.execute(statement.limit(10).offset(10 * (page - 1)))).scalars().all()

    allData = (await session.execute(statement)).scalars().all()
    countPage = math.ceil(len(allData) / 10)
    print(getLapoaran)
    return {
        "msg": "success",
        "data": {
            "data": getLapoaran,
            "count_data": len(getLapoaran),
            "count_page": countPage
        }
    }

async def getLaporanPkl(id_laporan: int, id_sekolah: int, session: AsyncSession) -> LaporanPklDudiBase:
    """
    Retrieve a specific PKL report.

    Args:
        id_laporan (int): The ID of the PKL report.
        id_sekolah (int): The school ID.
        session (AsyncSession): The database session.

    Returns:
        LaporanPklDudiBase: A dictionary containing the retrieved PKL report.

    Raises:
        HttpException: If the specified PKL report is not found.
    """
    findLaporanPkl = (await session.execute(select(LaporanPKL).options(joinedload(LaporanPKL.dudi), joinedload(LaporanPKL.pembimbing_dudi)).where(and_(LaporanPKL.id == id_laporan, LaporanPKL.dudi.has(Dudi.id_sekolah == id_sekolah))))).scalar_one_or_none()

    if not findLaporanPkl:
        raise HttpException(404, "laporan pkl tidak ditemukan")
    
    return {
        "msg": "success",
        "data": findLaporanPkl
    }