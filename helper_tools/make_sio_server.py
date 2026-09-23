

import socketio

redis_manager = socketio.AsyncRedisManager(
    url="redis://localhost:6379/0"
)


sio_server  = socketio.AsyncServer(
    client_manager=redis_manager,
    transports=["websocket", "polling"],
    async_mode="asgi",
    cors_allowed_origins=[
        "http://localhost:5000"
    ]
)