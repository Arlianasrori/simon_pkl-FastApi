from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_
from sqlalchemy.orm import subqueryload

# models
from ....models.notificationModel import Notification,NotificationRead
from ...models_domain.notification_model import NotificationModelBase,ResponseGetUnreadNotification

# common
from copy import deepcopy
from ....error.errorHandling import HttpException
from python_random_strings import random_strings

async def getAllNotification(id_pembimbing_dudi : int,session : AsyncSession) -> list[NotificationModelBase]:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.id_pembimbing_dudi == id_pembimbing_dudi))).where(Notification.id_pembimbing_dudi == id_pembimbing_dudi).order_by(desc(Notification.created_at)))).scalars().all()

    return {
        "msg" : "success",
        "data" : findNotification
    }

async def getNotificationById(id_notification : int,id_pembimbing_dudi : int,session : AsyncSession) -> NotificationModelBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.id_pembimbing_dudi == id_pembimbing_dudi))).where(and_(Notification.id == id_notification,Notification.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findNotification :
        raise HttpException(400,"notification tidak ditemukan")
    
    return {
        "msg" : "success",
        "data" : findNotification
    }

async def readNotification(id_notification : int,id_pembimbing_dudi : int,session : AsyncSession) -> NotificationModelBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.id_pembimbing_dudi == id_pembimbing_dudi))).where(and_(Notification.id == id_notification,Notification.id_pembimbing_dudi == id_pembimbing_dudi)))).scalar_one_or_none()

    if not findNotification :
        raise HttpException(400,"notification tidak ditemukan")
    
    if len(findNotification.reads) > 0 :
        raise HttpException(400,"notification sudah dibaca")
    
    notificationMapping = {
        "id" : random_strings.random_digits(6),
        "notification_id" : id_notification,
        "id_pembimbing_dudi" : id_pembimbing_dudi,
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

async def getCountNotification(id_pembimbing_dudi : int,session : AsyncSession) -> ResponseGetUnreadNotification:
    findNotification = (await session.execute(select(Notification).where(and_(Notification.id_pembimbing_dudi == id_pembimbing_dudi,~Notification.reads.any(NotificationRead.id_pembimbing_dudi == id_pembimbing_dudi))))).scalars().all()

    return {
        "msg" : "success",
        "data" : {
            "count" : len(findNotification)
        }
    }