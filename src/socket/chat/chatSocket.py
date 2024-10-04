from ...domain.chatting import chattingService
from ...domain.chatting.chattingModel import SendMessagebody,HandleChunkFileBody,CompleteUploadFileBody
from ...domain.models_domain.chat_model import RoomWithRoomUser,RoomWithRoomUserWithoutUser,MessageBase,MessageWithMedia

from ...db.db import SessionLocal
from ...error.errorHandling import HttpException
from pydantic import ValidationError

# socket
from ..socket import sio
from ..connectDisconnectSocket import online_users
from ..socker_error import socketError
from ..socketUtils import validation_middleware,delete_message as deleteMessageUtils

@sio.on("send_message")
async def send_message(sid,data):
    try :
        """
        body : 
        {
            access_token : str,
            type_user : str,
            "message" : {
                "room_id" : int,
                "message" : str,
                "receiver_id" : id,
                "receiver_type" : UserTypeEnum,
            }
        }
        """
        print(f"send messahe from : {data}")
        session = SessionLocal()
        auth = await validation_middleware(data,session)
        print(f"auth : {auth}")
        if not auth :
            return await socketError(401,"Unauthorized","Unauthorized",sid)
        
        message = data.get("message")
        message.update({"sender_id" : auth["user_id"],"sender_type" : auth["type_user"]})
        
        if not message :
            return await socketError(400,"message body is required","validation error",sid)
        
        messageValid = SendMessagebody(**message)
        
        sendMessage = await chattingService.sendMessage(messageValid,session)

        await sio.emit("send_message",{
            **sendMessage,
            "created_at" : sendMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at" : sendMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "type_user" : auth["type_user"].value,
        })
        # Looping untuk setiap pengguna online dan menemukan id_pengguna yang sama dengan receiver id
        for user in online_users.items():
            sid, user = user
            
            if user["user_id"] == sendMessage["receiver_id"] :
                await sio.emit("send_message",{
                    **sendMessage,
                    "created_at" : sendMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at" : sendMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "type_user" : user["type_user"].value,
                })
    
    except HttpException as e:
            # print(e)
            await socketError(e.status,e.messsage,"send_message",sid)
    except ValidationError as e:
        # print(e)
        await socketError(500,str(e),"send_message",sid)
    except Exception as e:
        # print(e)
        await socketError(500,str(e),"send_message",sid)
    finally :
        await session.close()

@sio.on("delete_message")
async def delete_message(sid,data):
    try :
        """
        body : 
        {
            access_token : str,
            type_user : str,
            message_id : int,
        }
        """
        session = SessionLocal()
        auth = await validation_middleware(data,session)
        if not auth :
            return await socketError(401,"Unauthorized","Unauthorized",sid)
        
        message_id = data.get("message_id")
        if not message_id :
            return await socketError(400,"message_id is required","validation error",sid)
        
        message_id = int(message_id)
        deleteMessage = await chattingService.delete_message(message_id,auth["user_id"],session)

        await sio.emit("delete_message",{
            **deleteMessage,
            "created_at" : deleteMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at" : deleteMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "type_user" : auth["type_user"].value,
        })
        
        # Looping untuk setiap pengguna online dan menemukan id_pengguna yang sama dengan receiver id
        for user in online_users.items():
            sid, user = user
            
            if user["user_id"] == deleteMessage["receiver_id"] :
                await sio.emit("delete_message",{
                    **deleteMessage,
                    "created_at" : deleteMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at" : deleteMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "type_user" : user["type_user"].value
                })
            
    except HttpException as e:
            # print(e)
            await socketError(e.status,e.messsage,"delete_message",sid)
    except ValidationError as e:
        # print(e)
        await socketError(500,str(e),"delete_message",sid)
    except Exception as e:
        # print(e)
        await socketError(500,str(e),"delete_message",sid)
    finally :
        await session.close()
        
        
@sio.on("update_message")
async def update_message(sid,data):
    try :
        """
        body : 
        {
            access_token : str,
            type_user : str,
            message_id : int,
            message : str,
        }
        """
        session = SessionLocal()
        auth = await validation_middleware(data,session)
        if not auth :
            return await socketError(401,"Unauthorized","Unauthorized",sid)
        
        message_id = data.get("message_id")
        if not message_id :
            return await socketError(400,"message_id is required","validation error",sid)
        
        message_id = int(message_id)
        
        message = data.get("message")
        if not message :
            return await socketError(400,"message is required","validation error",sid)
        
        updateMessage = await chattingService.update_message(message_id,message,auth["user_id"],session)

        await sio.emit("update_message",{
            **updateMessage,
            "created_at" : updateMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at" : updateMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "type_user" : auth["type_user"].value,
        })
        
        # Looping untuk setiap pengguna online dan menemukan id_pengguna yang sama dengan receiver id
        for user in online_users.items():
            sid, user = user
            
            if user["user_id"] == updateMessage["receiver_id"] :
                await sio.emit("update_message",{
                    **updateMessage,
                    "created_at" : updateMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at" : updateMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "type_user" : user["type_user"].value
                })
            
    except HttpException as e:
            # print(e)
            await socketError(e.status,e.messsage,"update_message",sid)
    except ValidationError as e:
        # print(e)
        await socketError(500,str(e),"update_message",sid)
    except Exception as e:
        # print(e)
        await socketError(500,str(e),"update_message",sid)
    finally :
        await session.close()
        

@sio.on("read_message")
async def read_message(sid,data):
    try :
        """
        body : 
        {
            access_token : str,
            type_user : str,
            message_id : int,
        }
        """
        session = SessionLocal()
        auth = await validation_middleware(data,session)
        if not auth :
            return await socketError(401,"Unauthorized","Unauthorized",sid)
        
        message_id = data.get("message_id")
        if not message_id :
            return await socketError(400,"message_id is required","validation error",sid)
        
        message_id = int(message_id)
        readMessage = await chattingService.read_message(message_id,auth["user_id"],session)

        await sio.emit("read_message",{
            **readMessage,
            "created_at" : readMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at" : readMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "type_user" : auth["type_user"].value,
        })
        
        # Looping untuk setiap pengguna online dan menemukan id_pengguna yang sama dengan receiver id
        for user in online_users.items():
            sid, user = user
            
            if user["user_id"] == readMessage["receiver_id"] :
                await sio.emit("read_message",{
                    **readMessage,
                    "created_at" : readMessage["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at" : readMessage["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "type_user" : user["type_user"].value
                })
            
    except HttpException as e:
            # print(e)
            await socketError(e.status,e.messsage,"read_message",sid)
    except ValidationError as e:
        # print(e)
        await socketError(500,str(e),"read_message",sid)
    except Exception as e:
        # print(e)
        await socketError(500,str(e),"read_message",sid)
    finally :
        await session.close()
        
# upload file
@sio.on("start_upload_file")
async def start_upload_file(sid,data):
    print("start")
    session = SessionLocal()
    dataValid = None
    try :
        """
        body : 
        {
            access_token : str,
            type_user : str,
            data : {
                message_id : int,
                file_name : str,
                chunk : list,
                offset : int,
                total_chunk : int,
                current_chunk : int,               
            }
        }
        """
        
        auth = await validation_middleware(data,session)

        if not auth :
            return await socketError(401,"tokennya bro","Unauthorized",sid)
        dataFile = data.get("data")
        
        if not dataFile :
            return await socketError(400,"data is required","validation error",sid)
        
        dataValid = HandleChunkFileBody(**dataFile)
        
        startUpload = await chattingService.start_upload_chunk(dataValid,session)
        
        print("emit")
        await sio.emit("start_upload_file",startUpload)
        
    except HttpException as e:
            # print(e)
            if dataValid and dataValid.message_id:
                await deleteMessageUtils(dataValid.message_id,session)
            await socketError(e.status,e.messsage,"start_upload_file",sid)
    except ValidationError as e:
        # print(e)
        if dataValid and dataValid.message_id:
            await deleteMessageUtils(dataValid.message_id,session)
        await socketError(500,str(e),"upload_file",sid)
    except Exception as e:
        # print(e)
        if dataValid and dataValid.message_id:
            await deleteMessageUtils(dataValid.message_id,session)
        await socketError(500,str(e),"start_upload_file",sid)
    finally :
        await session.close()
        
@sio.on("progress_upload_file")
async def progress_upload_file(sid,data):
    session = SessionLocal()
    dataValid = None
    try :
        """
        body : 
        {
            access_token : str,
            type_user : str,
            data : {
                message_id : int,
                file_name : str,
                chunk : list,
                offset : int,
                total_chunk : int,
                current_chunk : int,               
            }
        }
        """
        
        auth = await validation_middleware(data,session)
    
        if not auth :
            return await socketError(401,"tokennya bro","Unauthorized",sid)
        dataFile = data.get("data")
        
        if not dataFile :
            return await socketError(400,"data is required","validation error",sid)
        
        dataValid = HandleChunkFileBody(**dataFile)
        
        uploadChunk = await chattingService.handle_chunk_file(dataValid,session)
        
        await sio.emit("handle_chunk",uploadChunk)
        
    except HttpException as e:
        # print(e)
        if dataValid and dataValid.message_id:
            await deleteMessageUtils(dataValid.message_id,session)
        await socketError(e.status,e.messsage,"upload_file",sid)
    except ValidationError as e:
        # print(e)
        if dataValid and dataValid.message_id:
            await deleteMessageUtils(dataValid.message_id,session)
        await socketError(500,str(e),"upload_file",sid)
    except Exception as e:
        # print(e)
        if dataValid and dataValid.message_id:
            await deleteMessageUtils(dataValid.message_id,session)
        await socketError(500,str(e),"upload_file",sid)
    finally :
        await session.close()   

@sio.on("complete_upload_file")
async def complete_upload_file(sid,data):
    print("complete")
    session = SessionLocal()    
    dataValid = None
    try :
        """
        body : 
        {
            access_token : str,
            data : {
                message_id : int,
                file_name : str,
            }
        }
        """
        auth = await validation_middleware(data,session)
        if not auth :
            return await socketError(401,"Unauthorized","Unauthorized",sid)
        
        dataFile = data.get("data")
        
        if not dataFile :
            return await socketError(400,"data is required","validation error",sid)
        
        dataValid = CompleteUploadFileBody(**dataFile)
        
        completeUploadChunk = await chattingService.complete_upload_chunk(dataValid,session)
        
        await sio.emit("complete_upload_file",completeUploadChunk)
            
    except HttpException as e:
            print(e)
            # if dataValid and dataValid.message_id:
            #     await deleteMessageUtils(dataValid.message_id,session)
            await socketError(e.status,e.messsage,"upload_file",sid)
    except ValidationError as e:
        print(e)
        # if dataValid and dataValid.message_id:
        #     await deleteMessageUtils(dataValid.message_id,session)
        await socketError(500,str(e),"upload_file",sid)
    except Exception as e:
        print(e)
        # if dataValid and dataValid.message_id:
        #     await deleteMessageUtils(dataValid.message_id,session)
        await socketError(500,str(e),"upload_file",sid)
    finally :
        await session.close()  