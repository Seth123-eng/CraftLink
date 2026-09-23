
from quart import (
    Blueprint, request, url_for, redirect,
    session, jsonify
)

from quart_auth import AuthUser, login_user, logout_user

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time
from helper_tools.authenticated_clients_manager import login_required

from app_db_models.user_model import UserTable

from sqlalchemy import select

from app_factory import web_app

#from werkzeug.security import check_password_hash


import bleach


login_logout_bp = Blueprint("login_logout_bp", __name__)


@login_logout_bp.post("/auth/login")
async def handle_login():
    
    form = await request.form
    
    email = bleach.clean(
        str(form.get("email", "")).strip()
    )
    password = form.get("password", "")
    
    async with make_session() as sess:
        
        user = await sess.scalar(
            select(UserTable)
            .where(UserTable.email == email)
        )
        
        if not user:
            
            return jsonify({
                "success" : False,
                "message" : f"User does not exist, sign up instead.."
            })
        
        session["user_id"]=user.id
        session["email"]=email

        if user.account_status != "active":
            
            return jsonify({
                "success" : False,
                "redirect" : url_for("activate_account_bp.activate_account_page"),
            })

        if user.failed_login_attempts >= 5:
            
            return jsonify({
                "success" : False,
                "message" : f"Account locked, try again later."
            })
        
        if await web_app.bcrypt.async_check_password_hash(
            password=password,
            pw_hash=user.password_hash
        ):
            
        #if check_password_hash(
                #pwhash=user.password_hash,
                #password=password
            #):
            
            try:
                if user.failed_login_attempts > 0:
                    user.failed_login_attempts = 0  

                    await sess.commit()
                    
                    print("cleared failed login attempts")
                
            except Exception as e:
                
                await sess.rollback()
                
                print("Error while clearing failed login attempts")
                print(f"Exception = {e}")
            
            login_user(AuthUser(user.id))
            
            try:
                user.time_zone = session.get('zone_name', '')
                await sess.commit()
                print(f"Timezone updated")
            except Exception as e:
                print(f"Error while updating timezone = {e}")
                await sess.rollback()
            
            return jsonify({
                "success": True,
                "redirect" : url_for("dashboard_bp.dashboard")
            })
            
        try:
            user.failed_login_attempts += 1                
            await sess.commit()
            
            if user.failed_login_attempts >= 5:
                
                user.account_locked_datetime = await get_current_time()
                
                await sess.commit()
            
                return jsonify({
                    "success" : False,
                    "message" : f"Account locked, try again later."
                }) 
            

            print("registered an invalid login attempt")
            
        except Exception as e:
            
            await sess.rollback()
            
            print("failed to register an invalid login attempt")
            print(f"Exception = {e}")
            
        return jsonify({
            "success" : False,
            "message" : f"Invalid login credentials entered!!"
        })
        
        
        
@login_logout_bp.route("/logout")
@login_required
async def handle_logout():
    
    session.clear()
    logout_user()
    
    return redirect(url_for('timezone_bp.welcome_page'))