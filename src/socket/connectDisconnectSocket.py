import asyncio
from urllib.parse import parse_qs
from .socket_hear_beat import HeartbeatManager
from .socketUpdateOnline import updateIsOnlineUser
from .socker_error import socketError
from ..db.db import SessionLocal
from .socket import sio
from .socket_middleware import auth_middleware
from ..error.errorHandling import HttpException
from .socketUtils import forType
# Dictionary untuk menyimpan informasi pengguna yang sedang online
online_users = {}
# Inisialisasi HeartbeatManager untuk mengelola heartbeat pengguna
heartbeat_manager = HeartbeatManager(online_users, sio)

# Variabel untuk menyimpan task heartbeat
heartbeat_task = None

def connetDisconnectSocket() :
    # handle when client connect to socket
    @sio.on("connect")
    async def connect(sid, environ,auth = {}):
        session = SessionLocal()
        try :
            access_token_from_auth = auth.get("access_token")
            auth_header = None
            if access_token_from_auth :
                auth_header = access_token_from_auth
            else :
                headers = environ.get('asgi.scope', {}).get('headers', [])
                for name, value in headers:
                    if name.decode('utf-8').lower() == 'access_token':
                        auth_header = value.decode('utf-8')
                        break

            if not auth_header :
                return await socketError(401,"Unauthorized","Unauthorized",sid)

            # get type user from query params
            query_string = environ.get('QUERY_STRING')
            query_params = parse_qs(query_string)
            
            type_user_from_data = query_params.get("type_user")

            if not type_user_from_data :
                return await socketError(400,"Type User Is Required","Validation",sid)
            
            type_user = forType.get(type_user_from_data[0])
           
            if not type_user :
                return await socketError(401,"Unauthorized","Unauthorized",sid)
           
            # Melakukan autentikasi pengguna
            auth = await auth_middleware(auth_header,type_user,session)
            if not auth:
                # Mengembalikan error jika autentikasi gagal
                return await socketError(401,"Unauthorized","Unauthorized",sid)
            user_id = auth["user_id"]
            # Menyimpan informasi pengguna yang baru terhubung
            online_users[sid] = {
                "user_id" : user_id,
                "type_user" : type_user.value,
                "last_beat" : asyncio.get_event_loop().time()
            }
            print(f"connect : {sid}")
            # Memperbarui status online pengguna di database
            await updateIsOnlineUser(user_id, True,type_user,session)
            # Mengirim event bahwa pengguna telah online
            await sio.emit('user_online', {'user_id': user_id,"isOnline" : True,"type_user" : type_user.value})

            # Memulai heartbeat manager jika belum berjalan
            heartbeat_manager.start_if_not_running()
        except HttpException as e:
            # print(e)
            await socketError(e.status,e.messsage,"connect",sid)
        except Exception as e:
            # print(e)
            await socketError(500,str(e),"connect",sid)
        finally :
            # Menutup sesi database
            await session.close()

    # handle when client disconncet to socket
    @sio.on("disconnect")
    async def disconnect(sid):
        session = SessionLocal()
        # Membuat sesi database baru
        try :
            print("disconnect")
            user = online_users.get(sid)
            if user :
                # Menghapus pengguna dari daftar online
                del online_users[sid]
                # Memperbarui status offline pengguna di database
                await updateIsOnlineUser(user["user_id"], False,user["type_user"],session)
                # Mengirim event bahwa pengguna telah offline
                await sio.emit('user_offline', {'user_id': user['user_id'],"isOnline" : False,"type_user" : user["type_user"]})

            # Menghentikan heartbeat manager jika tidak ada pengguna online
            if not online_users:
                    await heartbeat_manager.stop()
        except Exception as e:
            await socketError(500,str(e),"connect",sid)
        finally :
            # Menutup sesi database
            await session.close()

    # handle when client send heartbeat to socket
    @sio.on("heartbeat")
    async def handle_heartbeat(sid):
        try :
            # print(f"hearbeat {sid}")
            # Membuat sesi database baru
            session = SessionLocal()
            if sid in online_users:
                # Memperbarui waktu heartbeat terakhir untuk pengguna
                online_users[sid].update({"last_beat" : asyncio.get_event_loop().time()})
                
        except Exception as e:
            await socketError(500,str(e),"connect",sid)
        finally :
            # Menutup sesi database
            await session.close()
            
# Fungsi untuk membersihkan sumber daya saat aplikasi ditutup
async def cleanup():
    try :
        await heartbeat_manager.stop()
    except Exception as e:
        print(e)
