from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,or_,not_
from sqlalchemy.orm import subqueryload

# models
from ....models.notificationModel import Notification,NotificationRead
from ...models_domain.notification_model import NotificationModelBase,ResponseGetUnreadNotification,ResponseGetAllNotification

# common
from ....error.errorHandling import HttpException
from python_random_strings import random_strings
from collections import defaultdict
from babel.dates import format_date
from babel import Locale

async def getAllNotification(id_siswa : int,id_dudi : int,session : AsyncSession) -> ResponseGetAllNotification :
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.id_siswa == id_siswa))).where(or_(Notification.id_siswa == id_siswa,Notification.id_dudi == id_dudi if id_dudi else False,and_(Notification.id_siswa == None,Notification.id_dudi == None,Notification.id_pembimbing_dudi == None,Notification.id_guru_pembimbing == None))).order_by(desc(Notification.created_at)))).scalars().all()

    grouped_notifications = defaultdict(list)
     # Membuat locale Indonesia
    locale_id = Locale('id', 'ID')
    for notification in findNotification:
        date_key = format_date(notification.created_at, format="EEEE, d MMMM yyyy", locale=locale_id)
        grouped_notifications[date_key].append(notification)

    # Mengubah defaultdict menjadi dict biasa untuk respons JSON
    grouped_data = dict(grouped_notifications)

    return {
        "msg" : "success",
        "data" : grouped_data
    }

async def getNotificationById(id_notification : int,id_siswa : int,id_dudi : int,session : AsyncSession) -> NotificationModelBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.id_siswa == id_siswa))).where(and_(Notification.id == id_notification,or_(Notification.id_siswa == id_siswa,Notification.id_dudi == id_dudi,and_(Notification.id_siswa == None,Notification.id_dudi == None,Notification.id_pembimbing_dudi == None,Notification.id_guru_pembimbing == None)))))).scalar_one_or_none()

    if not findNotification :
        raise HttpException(400,"notification tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findNotification
    }

async def readNotification(id_notification : int,id_siswa : int,id_dudi : int,session : AsyncSession) -> NotificationModelBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.id_siswa == id_siswa))).where(and_(Notification.id == id_notification,or_(Notification.id_siswa == id_siswa,Notification.id_dudi == id_dudi,and_(Notification.id_siswa == None,Notification.id_dudi == None,Notification.id_pembimbing_dudi == None,Notification.id_guru_pembimbing == None)))))).scalar_one_or_none()

    if not findNotification :
        raise HttpException(400,"notification tidak ditemukan")
    
    if len(findNotification.reads) > 0 :
        raise HttpException(400,"notification sudah dibaca")
    
    notificationMapping = {
        "id" : random_strings.random_digits(6),
        "notification_id" : id_notification,
        "id_siswa" : id_siswa,
        "is_read" : True
    }

    notifDictCopy = deepcopy(findNotification.__dict__)
    session.add(NotificationRead(**notificationMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : {
            **notifDictCopy,
            "reads" : [notificationMapping]
        }
    }

async def getCountNotification(id_siswa : int,id_dudi : int,session : AsyncSession) -> ResponseGetUnreadNotification:
    findNotification = (await session.execute(select(Notification).where(and_(or_(Notification.id_siswa == id_siswa,Notification.id_dudi == id_dudi,and_(Notification.id_siswa == None,Notification.id_dudi == None,Notification.id_pembimbing_dudi == None,Notification.id_guru_pembimbing == None)),not_(Notification.reads.any(NotificationRead.id_siswa == id_siswa)))))).scalars().all()

    return {
        "msg" : "success",
        "data" : {
            "count" : len(findNotification)
        }
    }