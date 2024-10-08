import socketio

# Inisialisasi server Socket.IO asinkron dengan berbagai konfigurasi
sio = socketio.AsyncServer(cors_allowed_origins=["http://127.0.0.1:5500"], cors_credentials=True, transports=['polling', 'websocket'], async_mode='asgi', async_handlers=True)
# Membungkus server Socket.IO dalam aplikasi ASGI
socket_app = socketio.ASGIApp(sio)
