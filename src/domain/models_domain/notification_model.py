from pydantic import BaseModel
from datetime import datetime

class NotificationReadModelBase(BaseModel):
    id : int
    is_read : bool

class NotificationModelBase(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    reads : list[NotificationReadModelBase] = []
    
class ResponseGetUnreadNotification(BaseModel):
    count : int

class ResponseGetAllNotification(BaseModel):
    msg : str
    data : dict[str,list[NotificationModelBase]]
