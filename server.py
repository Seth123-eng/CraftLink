
from app_factory import web_app

from quart import url_for, redirect

from helper_tools.db_helper import engine, Base

from quart_auth import Unauthorized

from helper_tools.blueprint_registration import register_all_blueprints


@web_app.before_serving
async def startup():
    
    await register_all_blueprints() #ensure blueprints are registered
    
    async with web_app.app_context():
        
        async with engine.begin() as conn:
            
            try:            
                await conn.run_sync(Base.metadata.create_all)
                #await conn.run_sync(Base.metadata.drop_all)
                print(f"Database tables created")
                
            except Exception as e:
                
                print(f"Exception={e}")
                

@web_app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@web_app.errorhandler(Unauthorized)
async def handle_unauthorized_users(e):
    print(f"Exception = {e}")    
    return redirect(url_for('timezone_bp.welcome_page'))


app = web_app

#if __name__ == "__main__":

#    web_app.run("localhost", 5000)