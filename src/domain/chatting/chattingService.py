from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload,subqueryload

# models
from .chattingModel import UserListBase,SendMessagebody,GetRoomListResponse,HandleChunkFileBody,CompleteUploadFileBody
from ..models_domain.chat_model import RoomWithRoomUser,RoomWithRoomUserWithoutUser,MessageBase,MessageWithMedia
from ...models.chatModel import Room,RoomUsers,Message,MediaMessage
from ...models.siswaModel import Siswa
from  ...models.pembimbingDudiModel import PembimbingDudi
from ...models.guruPembimbingModel import GuruPembimbing
from ...models.sekolahModel import Admin
from ...models.types import UserTypeEnum

# common
from copy import deepcopy
from ...error.errorHandling import HttpException
from python_random_strings import random_strings
from datetime import datetime
import os
from .chatting_utils import get_file_type

listUser = [
    {
        "type" : UserTypeEnum.SISWA,
        "model" : Siswa
    },
    {
        "type" : UserTypeEnum.GURU,
        "model" : GuruPembimbing
    },
    {
        "type" : UserTypeEnum.PEMBIMBING_DUDI,
        "model" : PembimbingDudi
    },
    {
        "type" : UserTypeEnum.ADMIN,
        "model" : Admin
    }
]

async def get_user_by_type(type_user):
    return next((item for item in listUser if item["type"] == type_user), None)

async def createRoom(user_list : list[UserListBase],session : AsyncSession) -> RoomWithRoomUserWithoutUser :
    # room mapping
    roomMapping = {
        "id" : random_strings.random_digits(6),
        "created_at" : datetime.utcnow(),
        "updated_at" : datetime.utcnow()
    } 
    
    # store to database
    session.add(Room(**roomMapping))
    
    # validate len of user list,just two item provided
    if len(user_list) != 2 or len(user_list) == 0 :
        raise HttpException(400,"user harus memiliki dua item atau tidak boleh kosong")
    
    # looping user list
    for user in user_list :
        # validasi user dengan pydantic
        userValid = UserListBase(user_type = user["user_type"],id = user['id'])
        
        # get user data by type
        user_data = await get_user_by_type(userValid.user_type)
        
        if user_data is None :
            raise HttpException(400,f"type user {user.user_type} tidak ditemukan")
        
        findUser = (await session.execute(select(user_data["model"]).where(user_data["model"].id == userValid.id))).scalar_one_or_none()
        
        if findUser is None :
            raise HttpException(400,f"User {user["id"]} tidak ditemukan")
        
        # room users mapping 
        roomUserMapping = {
            "id" : random_strings.random_digits(6),
            "user_id" : findUser.id,
            "room_id" : roomMapping["id"]
        }
        
        # store to database
        session.add(RoomUsers(**roomUserMapping))
        
    await session.commit()
        
    return {
        **roomMapping,
        "room_users" : roomUserMapping
    }
        
        
async def sendMessage(chat : SendMessagebody,session : AsyncSession) -> MessageBase:
    # cek apakah ada roo  id atau tidal
    if chat.room_id :
        # cek apakah room id ada atau tidak
        findRoom = (await session.execute(select(Room).where(Room.id == chat.room_id))).scalar_one_or_none()
        
        if findRoom is None :
            raise HttpException(400,f"room id {chat.room_id} tidak ditemukan")
    else :
        # cek apakah ada room id yang sudah ada atau tidak
        findRoom = (await session.execute(select(Room).where(and_(Room.room_users.any(RoomUsers.user_id == chat.sender_id),Room.room_users.any(RoomUsers.user_id == chat.receiver_id))))).scalar_one_or_none()
        
        if findRoom is None :
            lisUser = [
                {
                    "id" : chat.sender_id,
                    "user_type" : chat.sender_type
                },
                {
                    "id" : chat.receiver_id,
                    "user_type" : chat.receiver_type
                }
            ]
            print(lisUser)
                
            findRoom = await createRoom(lisUser,session)
    
    chatMapping = {
        "id" : random_strings.random_digits(6),
        "message" : chat.message,
        "room_id" : findRoom.id,
        "sender_id" : chat.sender_id,
        "receiver_id" : chat.receiver_id,
        "is_read" : False,
        "created_at" : datetime.utcnow(),
        "updated_at" : datetime.utcnow()
    }
    
    session.add(Message(**chatMapping))
    
    await session.commit()
    
    return chatMapping

async def getRommList(user_id : int,session : AsyncSession) -> list[GetRoomListResponse] :
    #  get roomUser list
    getRoomUsers = (await session.execute(select(RoomUsers).options(joinedload(RoomUsers.room),joinedload(RoomUsers.user)).where(RoomUsers.user_id == user_id))).scalars().all()
    
    print(getRoomUsers)
    
    rooms = [] # menampung list room untuk response
    
    for roomUser in getRoomUsers :
        # mengambil message terakhir dari room
        lastMessage = (await session.execute(select(Message).where(Message.room_id == roomUser.room_id).order_by(Message.created_at.desc()))).scalars().first()
        
        # mengambil data lawan chat yang berupa user
        getToUser = (await session.execute(select(RoomUsers).options(joinedload(RoomUsers.user)).where(and_(RoomUsers.room_id == roomUser.room_id,RoomUsers.user_id != user_id)))).scalar_one_or_none()
        
        # jika tidak ada room user maka skip
        if getToUser is None :
            continue
        
        # mengambil typeuser dari lawan chat
        toUserType = await get_user_by_type(getToUser.user.user_type)
        
        # mengambil data user lawan chat
        toUserData = (await session.execute(select(toUserType["model"]).where(toUserType["model"].id == getToUser.user_id))).scalar_one_or_none()
        
        print("te")
        # mengambil jumlah message yang tidak dibaca
        countNotReadMessage = (await session.execute(select(func.count(Message.id)).where(and_(Message.room_id == roomUser.room_id,Message.is_read == False,Message.receiver_id == user_id)))).scalar_one()
        
        # menambahkan data room ke list rooms
        rooms.append({
            "id_room": roomUser.room.id,
            "toUserName": toUserData.username if toUserType["type"] == UserTypeEnum.ADMIN else toUserData.nama,
            "toUser_type": getToUser.user.user_type,
            "toUser_foto_profile": None if toUserType["type"] == UserTypeEnum.ADMIN else toUserData.foto_profile,
            "toUser_id": toUserData.id,
            "last_message": lastMessage.message if lastMessage else "",
            "last_message_time": lastMessage.created_at if lastMessage else roomUser.room.updated_at,
            "count_not_read": countNotReadMessage
        })
        
    return rooms

async def getRoomById(user_id : str,room_id : str,session : AsyncSession) -> RoomWithRoomUser :
    # mengambil data room berdasarkan id room dan user id
    getRoom = (await session.execute(select(Room).options(joinedload(Room.room_users.and_(RoomUsers.user_id != user_id)).joinedload(RoomUsers.user)).where(Room.id == room_id))).scalars().first()

    if not getRoom :
        raise HttpException(404,"room tidak ditemukan")
    
    # mengambil typeuser dari lawan chat
    toUserType = await get_user_by_type(getRoom.room_users[0].user.user_type)
    
    # mengambil data user lawan chat
    toUserData = (await session.execute(select(toUserType["model"]).where(toUserType["model"].id == getRoom.room_users[0].user_id))).scalar_one_or_none()
    
    # mengambil data room user berupa dict
    roomUserdict = getRoom.room_users[0].__dict__
    
    # mengambil data room berupa dict
    roomDict = getRoom.__dict__
    
    return {
        **roomDict,
        "room_users" : {
            **roomUserdict,
            "user" : {
                "id" : toUserData.id,
                "nama" : toUserData.username if toUserType["type"] == UserTypeEnum.ADMIN else toUserData.nama,
                "foto_profile" : None if toUserType["type"] == UserTypeEnum.ADMIN else toUserData.foto_profile
            }
        }
    }
            
async def get_room_messages(user_id : int,room_id: str,session : AsyncSession) -> list[MessageWithMedia]:
    # get room and cek apakah ada atau tidak
    getRoom = (await session.execute(select(Room).where(and_(Room.id == room_id,Room.room_users.any(RoomUsers.user_id == user_id))))).scalar_one_or_none()

    if not getRoom :
        raise HttpException(404,"room tidak ditemukan") 
    
    # get message on room
    getMessageOnRoom = (await session.execute(select(Message).options(subqueryload(Message.media)).where(Message.room_id == room_id).order_by(Message.created_at.asc()))).scalars().all()

    return getMessageOnRoom

async def delete_message(message_id : int,user_id : int,session : AsyncSession) -> MessageBase :
    # get message and cek apakah ada atau tidak
    getMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()
    
    if not getMessage :
        raise HttpException(404,"message tidak ditemukan")
    
    # cek apakah message yang ingin didelete adalah message yang dikirimkan olehnya
    if getMessage.sender_id != user_id :
        raise HttpException(403,"anda tidak punya akses untuk menghapus message ini")
    
    # copy message before commit
    messageDictCopy = deepcopy(getMessage.__dict__)
    messageDictCopy.pop("_sa_instance_state")
    
    # delete message
    await session.delete(getMessage)
    await session.commit()
    
    return messageDictCopy
        
async def update_message(message_id : int,message : str,user_id : int,session : AsyncSession) -> MessageBase :
    # get message and cek apakah ada atau tidak
    getMessage = (await session.execute(select(Message).options(subqueryload(Message.media)).where(Message.id == message_id))).scalar_one_or_none()
    
    if not getMessage :
        raise HttpException(404,"message tidak ditemukan")
    
    # cek apakah message yang ingin diupdate adalah message yang dikirimkan olehnya
    if getMessage.sender_id != user_id :
        raise HttpException(403,"anda tidak punya akses untuk mengupdate message ini")
    
    # cek apakah message memiliki media atau tidak
    if len(getMessage.media) > 0 :
        raise HttpException(400,"messahe dengan media tidak dapat diupdate")
    
    # update message
    getMessage.message = message
    getMessage.updated_at = datetime.utcnow()
    
    # copy message before commit
    messageDictCopy = deepcopy(getMessage.__dict__)
    messageDictCopy.pop("_sa_instance_state")

    await session.commit()
    
    return messageDictCopy


async def read_message(message_id : int,user_id : int,session : AsyncSession) -> MessageBase :
    # get message and cek apakah ada atau tidak
    getMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()
    
    if not getMessage :
        raise HttpException(404,"message tidak ditemukan")
    
    # cek apakah message yang ingin didelete adalah message yang dikirimkan olehnya
    if getMessage.sender_id != user_id :
        raise HttpException(403,"anda tidak punya akses untuk menghapus message ini")
    
    getMessage.is_read = True
    # copy message before commit
    messageDictCopy = deepcopy(getMessage.__dict__)
    messageDictCopy.pop("_sa_instance_state")
    
    # delete message

    await session.commit()
    
    return messageDictCopy

FILE_STORE = os.getenv("DEV_CHATTING_FILE_STORE")
FILE_URL = os.getenv("DEV_CHATTING_FILE_BASE_URL")
FILE_BUFFERS = {
    
}

async def start_upload_chunk(file : HandleChunkFileBody,session : AsyncSession) :
    # get message and cek apakah ada atau tidak
    getMessage = (await session.execute(select(Message).where(Message.id == file.message_id))).scalar_one_or_none()
    
    if not getMessage :
        raise HttpException(404,"message tidak ditemukan")
    
    extSplit = file.file_name.split(".")
    extFile = extSplit[-1]
    
    if extFile not in ["jpg","png","jpeg","pdf","docx","xlsx","mp4","mp3","txt"] :
        raise HttpException(400,"file tidak didukung")
    
    fileName = f"{random_strings.random_digits(12)}-{file.file_name.split(' ')[-1]}"
    
    if fileName not in FILE_BUFFERS:
        # total chunk dapat diartikan sebagai berapa kali chunk akan dikirim atau split berapa kali file yang ada. misalnya 10 mb jika displit menjadi per 1 mb maka akan ada 10 chunk. dan byteArray dinit untuk untuk membuat tampungan berdasrakan total besaran file yang akan disimpan
        FILE_BUFFERS[fileName] = bytearray(file.total_chunk * len(file.chunk))
    
    # mengisi tampungan yang telah dibuat.offset adlaah posisi dari pecahan chunk saat ini.misalnya file 10 mb di split menjadi per 1 mb maka offset akan berubah setiap 1 mb.jadi ofset akan bertambah persatu mb dan chunk pada array akan ditulis untuk melanjutkan offset saat ini.misalnya offset 0 maka akan ditulis dari 0 sampai 1024 byte dan seteleah itu akan ditulsi dari 1024 byte sampai 2048 byte dan seterusnya
    FILE_BUFFERS[fileName][file.offset:file.offset+len(file.chunk)] = file.chunk
    print(FILE_BUFFERS[fileName])
    # menghitung progress berdasarkan chunk yang sudah dikirim.misal jika saat ini pecahan chunk 5 dan total pecahan 10 maka progresnya dalah 4 + 1 dibagi dengan totalnya dikali 100.jadi 6/10 * 100 = 60%
    progress = (file.current_chunk + 1) / file.total_chunk * 100
    
    # mengembalikan progress
    return {
        "fileName" : fileName,
        "progress" : progress,
        "current_chunk" : file.current_chunk + 1,
        "offset" : file.offset + len(file.chunk)
    }
    
async def handle_chunk_file(file : HandleChunkFileBody,session : AsyncSession) :
    # get message and cek apakah ada atau tidak
    getMessage = (await session.execute(select(Message).where(Message.id == file.message_id))).scalar_one_or_none()
    
    if not getMessage :
        raise HttpException(404,"message tidak ditemukan")
    
    extSplit = file.file_name.split(".")
    extFile = extSplit[-1]
    
    if extFile not in ["jpg","png","jpeg","pdf","docx","xlsx","mp4","mp3","txt"] :
        raise HttpException(400,"file tidak didukung")
    
    if file.file_name not in FILE_BUFFERS :
        raise HttpException(404,"file tidak ditemukan")
    
    # # mengisi tampungan yang telah dibuat.offset adlaah posisi dari pecahan chunk saat ini.misalnya file 10 mb di split menjadi per 1 mb maka offset akan berubah setiap 1 mb.jadi ofset akan bertambah persatu mb dan chunk pada array akan ditulis untuk melanjutkan offset saat ini.misalnya offset 0 maka akan ditulis dari 0 sampai 1024 byte dan seteleah itu akan ditulsi dari 1024 byte sampai 2048 byte dan seterusnya
    FILE_BUFFERS[file.file_name][file.offset:file.offset+len(file.chunk)] = file.chunk
    print(FILE_BUFFERS[file.file_name])
    progress = (file.current_chunk + 1) / file.total_chunk * 100
    
    return {
        "fileName" : file.file_name,
        "progress" : progress,
        "current_chunk" : file.current_chunk + 1,
        "offset" : file.offset + len(file.chunk)
    }
    
async def complete_upload_chunk(file : CompleteUploadFileBody,session : AsyncSession) :
    # get message and cek apakah ada atau tidak
    getMessage = (await session.execute(select(Message).where(Message.id == file.message_id))).scalar_one_or_none()
    
    if not getMessage :
        raise HttpException(404,"message tidak ditemukan")
    
    if file.file_name not in FILE_BUFFERS :
        raise HttpException(404,"file tidak ditemukan")
    
    fileType = await get_file_type(file.file_name.split(".")[-1])
    
    if not fileType :
        raise HttpException(400,"file tidak didukung")
    
    mediaMessageMapping = {
        "id" : random_strings.random_digits(6),
        "type" : fileType,
        "url" : f"{FILE_URL}/{file.file_name}",
        "message_id" : getMessage.id
    }
    
    session.add(MediaMessage(**mediaMessageMapping))
    
    filePath = f"{FILE_STORE}{file.file_name}"
    
    with open(filePath, 'wb') as f:
        f.write(FILE_BUFFERS[file.file_name])
        await session.commit()
    del FILE_BUFFERS[file.file_name]
    
    return mediaMessageMapping
