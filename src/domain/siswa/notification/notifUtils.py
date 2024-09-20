from ....models.pembimbingDudiModel import PembimbingDudi
# notification
from ...notification.notificationService import addNotification
    
from ....db.db import SessionLocal
from sqlalchemy import select
import asyncio
from python_random_strings import random_strings

async def AddNotifAfterPengajuan(id_dudi : int,nama_siswa : str,isCancelPkl : bool = False) :
    async with SessionLocal() as session :
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
            await addNotification(notifMapping,session)

def runningProccessSync(id_dudi : int,nama_siswa : str,iscancel : bool = False) :
    asyncio.run(AddNotifAfterPengajuan(id_dudi, nama_siswa,iscancel))