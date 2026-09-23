

from quart import Quart, request

from quart_bcrypt import Bcrypt
from quart_auth import QuartAuth

from config import Config

import uvicorn

import asyncio

import socketio

from helper_tools.make_sio_server import sio_server


def get_client_ip():
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.remote_addr


class WebApp():
    
    def __init__(self):
        
        self.quart_app_ = Quart(__name__, template_folder="templates")
        
        self.config = self.quart_app_.config
        self.register_blueprint = self.quart_app_.register_blueprint
        self.before_serving = self.quart_app_.before_serving
        self.after_serving = self.quart_app_.after_serving
        self.after_request = self.quart_app_.after_request
        self.app_context = self.quart_app_.app_context
        self.route = self.quart_app_.route
        self.get = self.quart_app_.get
        self.post = self.quart_app_.post
        self.errorhandler = self.quart_app_.errorhandler
        
        self.quart_app_.config.from_object(Config)
        
        self.bcrypt = Bcrypt()
        self.async_generate_password_hash = self.bcrypt.async_generate_password_hash
        self.async_check_password_hash = self.bcrypt.async_check_password_hash
        self.bcrypt.init_app(self.quart_app_)
        
        self.quart_auth_manager=QuartAuth()
        self.quart_auth_manager.init_app(self.quart_app_)

        self.sio_server_ = sio_server

        self.sio_quart_app = socketio.ASGIApp(
            socketio_server=self.sio_server_,
            other_asgi_app=self.quart_app_
        )
        
        
    async def run_(self, host:str, port:int):
        
        try:
            
            uvicorn_config = uvicorn.Config(
                self.sio_quart_app, host=host, port=port
            )
            server = uvicorn.Server(config=uvicorn_config)
            
            await server.serve()
            print("started uvicorn")
            
        except Exception as e:
            
            print(f"Exception = {e}")
            
    def run(self, host:str, port:int):
        
        try:
            asyncio.run(self.run_(host, port))
            print(f"started the event loop")
        except Exception as e:
            print("An exception while starting the event loop")
            print(f"Exception = {e}")
            
            
            
web_app = WebApp()