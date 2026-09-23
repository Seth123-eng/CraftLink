
from quart_auth import current_user

from quart import redirect, url_for, render_template

from helper_tools.db_helper import make_session

from functools import wraps

from app_db_models.user_model import UserTable

from app_factory import web_app

from sqlalchemy import select

import typing as t


async def get_current_user() -> UserTable|t.Any:
        
    async with web_app.app_context():
        
        async with make_session() as sess:

            if current_user.auth_id is not None:
            
                try:
                    user = await sess.scalar(
                        select(UserTable)
                        .where(
                            UserTable.id == int(current_user.auth_id),
                            UserTable.account_status == "active"
                        )
                    )                  
                    
                    if not user:
                        print("client not logged in")
                        return redirect(url_for('timezone_bp.welcome_page'))
                    
                    print("grabbed the current user🎉🎉")
                    
                except Exception as e:
                    
                    print("unable to grab the currently logged in client")
                    print(f"Exception = {e}")

                    user = None
                    
                    return redirect(url_for('timezone_bp.welcome_page'))
            else:
                return redirect(url_for('timezone_bp.welcome_page'))
        
    return user



def login_required(func):
    
    @wraps(func)
        
    async def decorated_func(*args, **kwargs):

        async with make_session() as sess:

            if current_user.auth_id is not None:
            
                try:
                    user = await sess.scalar(
                        select(UserTable)
                        .where(
                            UserTable.id == int(current_user.auth_id),
                            UserTable.account_status == "active"
                        )
                    )

                    if not user:
                        return redirect(url_for('timezone_bp.welcome_page'))
            
                    print("User with the role found. 🎉🎉")

                except Exception as e:

                    print(f"Exception = {e}")

                    return await render_template("not_authorised.html")
            else:
                return redirect(url_for('timezone_bp.welcome_page'))
        
        return await func(*args, **kwargs)
    
    return decorated_func




def admin_required(func):
    
    @wraps(func)
        
    async def decorated_func(*args, **kwargs):

        async with make_session() as sess:

            if current_user.auth_id is not None:
            
                try:
                    admin = await sess.scalar(
                        select(UserTable)
                        .where(
                            UserTable.id == int(current_user.auth_id),
                            UserTable.account_type == "admin",
                            UserTable.account_status == "active"
                        )
                    )

                    if not admin:
                        return redirect(url_for('timezone_bp.welcome_page'))
            
                    print("User with the role found. 🎉🎉")

                except Exception as e:

                    print(f"Exception = {e}")

                    return await render_template("not_authorised.html")
            else:
                return redirect(url_for('timezone_bp.welcome_page'))
        
        return await func(*args, **kwargs)
    
    return decorated_func



def client_required(func):
    
    @wraps(func)
        
    async def decorated_func(*args, **kwargs):

        async with make_session() as sess:

            if current_user.auth_id is not None:
            
                try:
                    admin = await sess.scalar(
                        select(UserTable)
                        .where(
                            UserTable.id == int(current_user.auth_id),
                            UserTable.account_type == "client",
                            UserTable.account_status == "active"
                        )
                    )

                    if not admin:
                        return redirect(url_for('timezone_bp.welcome_page'))
            
                    print("User with the role found. 🎉🎉")

                except Exception as e:

                    print(f"Exception = {e}")

                    return await render_template("not_authorised.html")
            else:
                return redirect(url_for('timezone_bp.welcome_page'))
        
        return await func(*args, **kwargs)
    
    return decorated_func




def technician_required(func):
    
    @wraps(func)
        
    async def decorated_func(*args, **kwargs):

        async with make_session() as sess:

            if current_user.auth_id is not None:
            
                try:
                    admin = await sess.scalar(
                        select(UserTable)
                        .where(
                            UserTable.id == int(current_user.auth_id),
                            UserTable.account_type == "technician",
                            UserTable.account_status == "active"
                        )
                    )

                    if not admin:
                        return redirect(url_for('timezone_bp.welcome_page'))
            
                    print("User with the role found. 🎉🎉")

                except Exception as e:

                    print(f"Exception = {e}")

                    return await render_template("not_authorised.html")
            else:
                return redirect(url_for('timezone_bp.welcome_page'))
        
        return await func(*args, **kwargs)
    
    return decorated_func