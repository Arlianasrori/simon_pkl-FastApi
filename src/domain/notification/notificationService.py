from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# models
from ...models.notificationModel import Notification,NotificationData
from .notificationModel import AddNotificationModel,AddDataNotificationModel
from ...models.siswaModel import Siswa
from ...models.dudiModel import Dudi
from ...models.pembimbingDudiModel import PembimbingDudi
from ...models.guruPembimbingModel import GuruPembimbing

# common
from ...error.errorHandling import HttpException
from enum import Enum
from ...db.db import SessionLocal

# FCM
import firebase_admin
from firebase_admin import credentials, messaging
import os

# Inisialisasi SDK dengan file kunci layanan Anda
cred = credentials.Certificate(os.getenv("FCM_PATH_KEY"))
firebase_admin.initialize_app(cred)

class UserType(Enum):
    SISWA = "siswa"
    PEMBIMBING_DUDI = "pembimbing_dudi"
    GURU_PEMBIMBING = "guru_pembimbing"

async def addNotification(data : AddNotificationModel,data_notification : AddDataNotificationModel | None = None) -> None:
    async with SessionLocal() as session :
        try :
            data = AddNotificationModel(**data)
            if data_notification :
                data_notification = AddDataNotificationModel(**data_notification)
                dataNotificationMapping = data_notification.model_dump()
                dataNotificationMapping["id_notification"] = data.id

            token_FCM = None
            id = None
            userType : UserType = None

            if data.id_siswa :
                findSiswa = (await session.execute(select(Siswa).where(Siswa.id == data.id_siswa))).scalar_one_or_none()
                print(findSiswa)

                if not findSiswa :
                    raise HttpException(400,"siswa tidak ditemukan")
                
                token_FCM = findSiswa.token_FCM
                id = findSiswa.id
                userType = UserType.SISWA

            elif data.id_pembimbing_dudi:
                findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id == data.id_pembimbing_dudi))).scalar_one_or_none()


                if not findPembimbingDudi :
                    raise HttpException(400,"pembimbing dudi tidak ditemukan")
                
                token_FCM = findPembimbingDudi.token_FCM
                id = findPembimbingDudi.id
                userType = UserType.PEMBIMBING_DUDI

            elif data.id_guru_pembimbing:
                findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == data.id_guru_pembimbing))).scalar_one_or_none()

                if not findGuruPembimbing :
                    raise HttpException(400,"guru pembimbing tidak ditemukan")
                token_FCM = findGuruPembimbing.token_FCM
                id = findGuruPembimbing.id
                userType = UserType.GURU_PEMBIMBING

            elif data.id_dudi:
                findDudi = (await session.execute(select(Dudi).where(Dudi.id == data.id_dudi))).scalar_one_or_none()

                if not findDudi :
                    raise HttpException(400,"dudi tidak ditemukan")
                
            session.add(Notification(**data.model_dump()))
            if data_notification :
                session.add(NotificationData(**dataNotificationMapping))

            await session.commit()
            await session.reset()
            if token_FCM and id :
                await kirim_pesan_fcm(token_FCM, data.title, data.body, userType, id)
        except Exception as e:
            print(f"Terjadi kesalahan: pada notificationService.py {e.args}")
        finally :
            await session.close()
 

async def kirim_pesan_fcm(token_FCM, title, body,userType : UserType, id):
    try:
        session = SessionLocal()
        if token_FCM :
            pesan = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                token=token_FCM,
            )
            response = messaging.send(pesan)
            print(f"Pesan berhasil dikirim: {response}")
            
    except Exception as e:
        # jika ada kesalahan pada token fcmUser maka akan dihapus dan dapat diupdate kembali
        if userType == UserType.SISWA:
            findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id))).scalar_one_or_none()

            if findSiswa :
                findSiswa.token_fcm = None
                await session.commit()
        elif userType == UserType.PEMBIMBING_DUDI:
            findPembimbingDudi = (await session.execute(select(PembimbingDudi).where(PembimbingDudi.id == id))).scalar_one_or_none()

            if findPembimbingDudi :
                findPembimbingDudi.token_fcm = None
                await session.commit()
        elif userType == UserType.GURU_PEMBIMBING:
            findGuruPembimbing = (await session.execute(select(GuruPembimbing).where(GuruPembimbing.id == id))).scalar_one_or_none()

            if findGuruPembimbing :
                findGuruPembimbing.token_fcm = None
                await session.commit()           
        print(f"Terjadi kesalahan: {e}")
    finally :
        await session.close()