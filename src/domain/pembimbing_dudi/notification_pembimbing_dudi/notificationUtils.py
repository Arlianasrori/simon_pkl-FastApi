# notification
import asyncio
from ...notification.notificationService import addNotification
from ....models.notificationModel import DataTypeNotificationEnum

# common
from python_random_strings import random_strings

async def AddNotifAfterPengajuan(id_siswa : int,title : str,body : str,id_pengajuan : int | None) :
    notifMapping = {
        "id" : random_strings.random_digits(6),
        "id_siswa" : id_siswa,
        "title" : title,
        "body" : body,
    }

    if id_pengajuan :
        dataNotification = {
            "data_type" : DataTypeNotificationEnum.PENGAJUAN,
            "data_id" : id_pengajuan
        }

    await addNotification(notifMapping,dataNotification)

def runningProccessSync(id_siswa : int,title : str,body : str,id_pengajuan : int | None = None) :
    asyncio.run(AddNotifAfterPengajuan(id_siswa,title,body,id_pengajuan))
