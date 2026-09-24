
from quart_auth import current_user

from quart import redirect, url_for, render_template

from helper_tools.db_helper import make_session

from functools import wraps

from app_db_models.user_model import UserTable

from sqlalchemy import select


async def get_current_user() -> UserTable|None:
        
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
                    return None
                return user
                
            except Exception as e:
                
                print("unable to grab the currently logged in client")
                print(f"Exception = {e}")

                return None
        else:
            return None


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