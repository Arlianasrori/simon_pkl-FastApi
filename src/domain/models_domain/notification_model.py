from pydantic import BaseModel
from datetime import datetime
from ...models.notificationModel import DataTypeNotificationEnum

class NotificationDataBase(BaseModel) :
    id_notification : int
    data_type : DataTypeNotificationEnum
    data_id : int
    
class NotificationReadModelBase(BaseModel):
    id : int
    is_read : bool

class NotificationModelBase(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    reads : list[NotificationReadModelBase] = []
    
class NotificationWithData(NotificationModelBase) :
    data : NotificationDataBase | None = None
    
class ResponseGetUnreadNotification(BaseModel):
    count : int

class ResponseGetAllNotification(BaseModel):
    msg : str
    data : dict[str,list[NotificationModelBase]]
