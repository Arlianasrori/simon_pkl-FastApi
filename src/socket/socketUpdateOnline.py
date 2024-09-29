from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.siswaModel import Siswa
from ..models.guruPembimbingModel import GuruPembimbing
from ..models.pembimbingDudiModel import PembimbingDudi
from ..models.sekolahModel import Admin
from ..models.types import UserTypeEnum

async def updateIsOnlineUser(id_user : str,isOnline : bool,typeUser,session : AsyncSession):
    try :
        if typeUser == UserTypeEnum.SISWA    :
            findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id_user))).scalar_one_or_none()
            findSiswa.is_online = isOnline
            await session.commit()
        elif typeUser == UserTypeEnum.GURU :
            findGuru = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == id_user))).scalar_one_or_none()
            findGuru.is_online = isOnline
            await session.commit()
        elif typeUser == UserTypeEnum.PEMBIMBING_DUDI :
            findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id == id_user))).scalar_one_or_none()
            findPembimbingDudi.is_online = isOnline
            await session.commit()
        elif typeUser == UserTypeEnum.ADMIN :
            findAdmin = (await session.execute(select(Admin).where(Admin.id == id_user))).scalar_one_or_none()
            findAdmin.is_online = isOnline
            await session.commit()
    finally :
        await session.close()