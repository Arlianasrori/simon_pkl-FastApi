from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from sqlalchemy.orm import joinedload

# models
from .laporanPklSiswaModel import ResponseLaporanPklSiswaPag, FilterLaporanPklSiswaQuery
from ...models_domain.laporan_pkl_dudi_model import LaporanPklDudiBase
from ....models.laporanPklModel import LaporanSiswaPKL
from ....models.sekolahModel import TahunSekolah
from ....models.siswaModel import Siswa

# common
import math
import datetime
from ....error.errorHandling import HttpException

async def getAllLaporanPkl(page: int | None, id_sekolah: int, id_tahun: int, query: FilterLaporanPklSiswaQuery | None, session: AsyncSession) -> ResponseLaporanPklSiswaPag:
    """
    Retrieves all LaporanSiswaPKL records based on the provided parameters.

    Parameters:
    - page (int): The page number for pagination.
    - id_sekolah (int): The ID of the sekolah.
    - id_tahun (int): The ID of the tahun.
    - query (FilterLaporanPklSiswaQuery | None): The query parameters for filtering the results.
    - session (AsyncSession): The asynchronous session object.

    Returns:
    - ResponseLaporanPklSiswaPag: The response object containing the paginated LaporanSiswaPKL records.

    Raises:
    - HttpException: If the tahun is not found.
    """
    findTahun = (await session.execute(select(TahunSekolah).where(TahunSekolah.id == id_tahun))).scalar_one_or_none()

    if not findTahun:
        raise HttpException(404, "tahun tidak ditemukan")
    
    if query.month or query.year:
        now = datetime.datetime.now()
        startQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 1, 1)
        endQuery = datetime.date(query.year if query.year else now.year, query.month if query.month else 12, 31)
        print(startQuery)
    
    getLaporan = (await session.execute(select(LaporanSiswaPKL).options(joinedload(LaporanSiswaPKL.siswa), joinedload(LaporanSiswaPKL.dudi)).where(and_(and_(LaporanSiswaPKL.tanggal >= startQuery, LaporanSiswaPKL.tanggal <= endQuery)) if query.month else True, LaporanSiswaPKL.tanggal == query.tanggal if query.tanggal else True, LaporanSiswaPKL.siswa.has(id_sekolah == id_sekolah), LaporanSiswaPKL.id_siswa == query.id_siswa if query.id_siswa else True).limit(10).offset(10 * (page - 1)))).scalars().all()

    conntData = (await session.execute(func.count(LaporanSiswaPKL.id))).scalar_one()
    countPage = math.ceil(conntData / 10)
    
    return {
        "msg": "success",
        "data": {
            "data": getLaporan,
            "count_data": len(getLaporan),
            "count_page": countPage
        }
    }

async def getLaporanPkl(id_laporan: int, id_sekolah: int, session: AsyncSession) -> LaporanPklDudiBase:
    """
    Retrieves a specific LaporanSiswaPKL record based on the provided ID.

    Parameters:
    - id_laporan (int): The ID of the laporan pkl.
    - id_sekolah (int): The ID of the sekolah.
    - session (AsyncSession): The asynchronous session object.

    Returns:
    - LaporanPklDudiBase: The response object containing the LaporanSiswaPKL record.

    Raises:
    - HttpException: If the laporan pkl is not found.
    """
    findLaporanPkl = (await session.execute(select(LaporanSiswaPKL).options(joinedload(LaporanSiswaPKL.siswa), joinedload(LaporanSiswaPKL.dudi)).where(and_(LaporanSiswaPKL.id == id_laporan, LaporanSiswaPKL.siswa.has(Siswa.id_sekolah == id_sekolah))))).scalar_one_or_none()
    print(findLaporanPkl)

    if not findLaporanPkl:
        raise HttpException(404, "laporan pkl tidak ditemukan")
    
    return {
        "msg": "success",
        "data": findLaporanPkl
    }
