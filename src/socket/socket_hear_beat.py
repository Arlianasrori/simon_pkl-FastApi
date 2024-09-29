import asyncio
from .socketUpdateOnline import updateIsOnlineUser
from ..db.db import SessionLocal
from .socker_error import socketError


session = SessionLocal()

class HeartbeatManager:
    # Interval waktu (dalam detik) antara setiap pemeriksaan heartbeat
    HEARTBEAT_INTERVAL = 10
    # Batas waktu (dalam detik) sebelum pengguna dianggap offline jika tidak ada heartbeat
    HEARTBEAT_TIMEOUT = 5

    def __init__(self, online_users, sio):
        # Dictionary untuk menyimpan informasi pengguna online
        self.online_users = online_users
        # Instance Socket.IO server
        self.sio = sio
        # Task asyncio untuk menjalankan loop heartbeat
        self.task = None

    async def heartbeat(self):
        print("heartbeat")
        while True:
            try:
                if len(self.online_users) == 0 :
                    print("pause hearbeat because no user online")
                    break
                # Menunggu selama interval heartbeat sebelum pemeriksaan berikutnya
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                # Mendapatkan waktu saat ini
                current_time = asyncio.get_event_loop().time()
                # List untuk menyimpan pengguna yang akan dianggap offline
                offline_users = []
                print(f"user online{self.online_users}")
                
                # Memeriksa setiap pengguna dalam dictionary online_users
                for userItem in self.online_users.items():
                    sid, user = userItem
                    # Jika waktu sejak heartbeat terakhir melebihi batas, anggap pengguna offline
                    if current_time - user['last_beat'] > self.HEARTBEAT_INTERVAL + self.HEARTBEAT_TIMEOUT:
                        print("user offline")
                        offline_users.append({"sid": sid, "user_id": user["user_id"],"type_user" : user["type_user"]})

                # Memproses pengguna yang dianggap offline
                print(f"offline user {offline_users}")
                for user in offline_users:
                    print("masuk offline")
                    # Menghapus pengguna dari dictionary online_users
                    del self.online_users[user["sid"]]
                    # Memperbarui status pengguna menjadi offline di database
                    await updateIsOnlineUser(user["user_id"], False,user["type_user"], session)
                    # Mengirim event 'user_offline' ke semua klien
                    await self.sio.emit('user_offline', {'user_id': user["user_id"],"isOnline" : False,"type_user" : user["type_user"]})
            
            except Exception as e:
                await socketError(500,"Internal Server Error","online_user",user["sid"])
                
            finally:
                # Memastikan sesi database ditutup setelah setiap iterasi
                await session.close()

    def start_if_not_running(self):
        # Memulai task heartbeat jika belum berjalan atau sudah selesai
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.heartbeat())

    async def stop(self):
        # Menghentikan task heartbeat jika sedang berjalan
        if self.task and not self.task.done():
            # Membatalkan task
            self.task.cancel()
            try:
                # Menunggu task selesai dibatalkan
                await self.task
            except asyncio.CancelledError:
                # Menangani error pembatalan task
                pass
            # Mengatur task kembali ke None
            self.task = None