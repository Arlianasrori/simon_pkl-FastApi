# notification
import asyncio
from ...notification.notificationService import addNotification

# common
from python_random_strings import random_strings

# db
from ....db.db import SessionLocal

async def AddNotifAfterPengajuan(id_siswa : int,title : str,body : str) :
    async with SessionLocal() as session :
        notifMapping = {
            "id" : random_strings.random_digits(6),
            "id_siswa" : id_siswa,
            "title" : title,
            "body" : body,
        }

        await addNotification(notifMapping,session)

def runningProccessSync(id_siswa : int,title : str,body : str) :
    asyncio.run(AddNotifAfterPengajuan(id_siswa,title,body))
