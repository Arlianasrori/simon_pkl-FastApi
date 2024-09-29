from fastapi import APIRouter,Depends

from ..domain.chatting import chattingService
from ..domain.chatting.chattingModel import UserListBase,SendMessagebody,GetRoomListResponse
from ..domain.models_domain.chat_model import RoomWithRoomUser,RoomWithRoomUserWithoutUser,MessageBase,MessageWithMedia

from ..auth.dependsAuthMiddleware.user.depend_auth_user import userDependAuth
from ..auth.dependsAuthMiddleware.user.get_user_auth import getUserAuth
from ..models.responseModel import ResponseModel
from ..db.sessionDepedency import sessionDepedency

# running chat socket
from ..socket.chat import chatSocket

chatRouter = APIRouter(prefix="/chat",dependencies=[Depends(userDependAuth)])

@chatRouter.get("/room",response_model=ResponseModel[list[GetRoomListResponse]],tags=["CHAT"])
async def getRoomList(user : dict = Depends(getUserAuth),Session: sessionDepedency = None) :
    roomList = await chattingService.getRommList(user["id"],Session)
    return {
        "msg" : "success",
        "data" : roomList
    }

@chatRouter.get("/room/{id_room}",response_model=ResponseModel[RoomWithRoomUser],tags=["CHAT"])
async def getRoomDetail(id_room : int,user : dict = Depends(getUserAuth),Session: sessionDepedency = None) :
    roomDetail = await chattingService.getRoomById(user["id"],id_room,Session)
    return {
        "msg" : "success",
        "data" : roomDetail
    }

@chatRouter.get("/room/{id_room}/message",response_model=ResponseModel[list[MessageWithMedia]],tags=["CHAT"])
async def getMessage(id_room : int,user : dict = Depends(getUserAuth),Session: sessionDepedency = None) :
    message = await chattingService.get_room_messages(user["id"],id_room,Session)
    return {
        "msg" : "success",
        "data" : message
    }