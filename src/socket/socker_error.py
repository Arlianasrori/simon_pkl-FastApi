from .socket import sio

async def socketError(status : int,msg : str,type : str,sid : str) :
    print(f"msg from error : {msg}")
    # await sio.send(data={"status" : status,"msg" : msg,"type" : type},to=sid,namespace="socket_error")
    await sio.emit("socket_error",{"status" : status,"msg" : msg,"type" : type},sid)