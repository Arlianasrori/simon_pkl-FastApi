from pydantic import BaseModel
from datetime import datetime 

class RoomBase(BaseModel) :
    id : int
    created_at : datetime
    updated_at : datetime

class UserBase(BaseModel) :
    id : int
    nama : str
    foto_profile : str | None = None
    
class RoomUserBase(BaseModel) :
    id : int
    user_id : int
    room_id : int
    
class RoomUserWithUser(RoomUserBase) :
    user : UserBase

class RoomWithRoomUser(RoomBase) :
    room_users : RoomUserWithUser 

class RoomWithRoomUserWithoutUser(RoomBase) :
    room_users : list[RoomUserBase] = []

class MessageBase(BaseModel) :
    id : int
    message : str
    sender_id : int
    receiver_id : int
    room_id : int
    is_read : bool
    created_at : datetime
    updated_at : datetime
    
class MediaMessageBase(BaseModel) :
    id : int
    type : str
    url : str

class MessageWithMedia(MessageBase) :
    media : list[MediaMessageBase] = []