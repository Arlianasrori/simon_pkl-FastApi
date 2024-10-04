from pydantic import BaseModel
from ...models.types import UserTypeEnum
from datetime import datetime

class UserListBase(BaseModel):
    id : int
    user_type : UserTypeEnum

class SendMessagebody(BaseModel) :
    room_id : int | None = None
    message : str
    sender_id : int
    sender_type : UserTypeEnum
    receiver_id : int
    receiver_type : UserTypeEnum

class GetRoomListResponse(BaseModel) :
    id_room : int
    toUserName : str
    toUser_id : int
    toUser_type : UserTypeEnum
    toUser_foto_profile : str | None = None
    last_message : str
    last_message_time : datetime
    count_not_read : int
    
class HandleChunkFileBody(BaseModel) :
    message_id : int
    file_name : str
    chunk : bytes
    offset : int
    total_chunk : int
    current_chunk : int

class CompleteUploadFileBody(BaseModel) :
    message_id : int
    file_name : str