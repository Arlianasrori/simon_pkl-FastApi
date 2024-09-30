from ..models.types import UserTypeEnum
from sqlalchemy.ext.asyncio import AsyncSession
from .socket_middleware import auth_middleware
from sqlalchemy import select
from ..models.chatModel import Message


forType = {
    "siswa" : UserTypeEnum.SISWA,
    "guru" : UserTypeEnum.GURU,
    "pembimbing_dudi" : UserTypeEnum.PEMBIMBING_DUDI,
    "admin" : UserTypeEnum.ADMIN,
}

async def validation_middleware(data,session : AsyncSession):
    # check if auth is not dict
    if not data or type(data) != dict:
        return False

    # get auth token
    auth_header = data.get('access_token')
    
    if not auth_header :
        return False
    
    # get type user
    type_user_from_data = data.get("type_user")
    type_user = forType.get(type_user_from_data)
    
    if not type_user :
        return False
    # Melakukan autentikasi pengguna
    auth = await auth_middleware(auth_header,type_user,session)
    if not auth:
        # Mengembalikan error jika autentikasi gagal
        return False

    return auth

async def delete_message(message_id,session : AsyncSession):
    findMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()
    if not findMessage :
        return False
    await session.delete(findMessage)
    await session.commit()
    return True