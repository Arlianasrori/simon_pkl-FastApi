from ....models.pembimbingDudiModel import PembimbingDudi
# notification
from ...notification.notificationService import addNotification
from ...notification.notificationModel import DataTypeNotificationEnum

from ....db.db import SessionLocal
from sqlalchemy import select
import asyncio
from python_random_strings import random_strings

async def AddNotifAfterPengajuan(id_dudi : int,nama_siswa : str,isCancelPkl : bool = False,id_pengajuan : int | None = None) :
    async with SessionLocal() as session :
        try :
            findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id_dudi == id_dudi))).scalars().all()

            for pembimbing in findPembimbingDudi :            
                if isCancelPkl :
                    notifMapping = {
                        "id" : random_strings.random_digits(6),
                        "id_pembimbing_dudi" : pembimbing.id,
                        "title" : "Informasi Untukmu!",
                        "body" : f"{nama_siswa} telah melakukan pengajuan cancel PKL",
                    }
                else :
                    notifMapping = {
                        "id" : random_strings.random_digits(6),
                        "id_pembimbing_dudi" : pembimbing.id,
                        "title" : "Kabar Baik!",
                        "body" : f"{nama_siswa} telah melakukan pengajuan PKL",
                    }
                if id_pengajuan :
                    dataNotification = {
                        "data_type" : DataTypeNotificationEnum.PENGAJUAN,
                        "data_id" : id_pengajuan
                    }
                await addNotification(notifMapping,dataNotification if dataNotification else None)
        finally :
            await session.close()

def runningProccessSyncPengajuan(id_dudi : int,nama_siswa : str,iscancel : bool = False,id_pengajuan : int | None = None) :
    asyncio.run(AddNotifAfterPengajuan(id_dudi, nama_siswa,iscancel,id_pengajuan))


async def AddNotifAfterAbsen(id_siswa : int,id_absen : int,keteranganAbsen : str) :  
    notifMapping = {
        "id" : random_strings.random_digits(6),
        "id_siswa" : id_siswa,
        "title" : "Kabar Baik!",
        "body" : f"kamu berhasil untuk melakukan absen {keteranganAbsen}",
    }
    if id_absen :
        dataNotification = {
            "data_type" : DataTypeNotificationEnum.ABSEN,
            "data_id" : id_absen
        }
    await addNotification(notifMapping,dataNotification if dataNotification else None)

def runningProccessSyncAbsen(id_siswa : int,id_absen : int,keteranganAbsen : str) :
    asyncio.run(AddNotifAfterPengajuan(id_siswa, id_absen,keteranganAbsen))