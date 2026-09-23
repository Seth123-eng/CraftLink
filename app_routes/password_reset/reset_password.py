

from quart import (
    Blueprint, render_template, jsonify,
    request, url_for, session
)


from helper_tools.db_helper import make_session
from helper_tools.web_security import (
    encode_with_itsdangerous_timed, decode_with_itsdangerous_timed,
    password_maker
)
from helper_tools.email_handling.email_sending import send_email_link

from app_db_models.user_model import UserTable

from sqlalchemy import select


import asyncio



reset_password_bp = Blueprint('reset_password_bp', __name__)


@reset_password_bp.route('/reset-password', methods=['GET'])
async def reset_password_page():
    return await render_template('auth_pages/reset_password.html')



@reset_password_bp.post('/send-reset/password-email')
async def send_reset_password_email():
    
    async with make_session() as sess:
        
        form = await request.form
        
        try:
            email = form.get("email", "")
            
            if not email:
                return jsonify({
                    "success" : False,
                    "message" : "Please enter your email address"
                })
            
            user = await sess.scalar(
                select(UserTable)
                .where(
                    UserTable.email == email
                )
            )

            if not user:

                return jsonify({
                    "success" : True,
                    "msg" : "Account does not exist"
                })

            asyncio.create_task(
                send_email_link(
                    email=email,
                    reason="reset_password",
                    link=url_for(
                        "reset_password_bp.account_recovery_page",
                        _external = True,
                        token_=encode_with_itsdangerous_timed(user.id)
                    )
                )
            )
            
            return jsonify({
                "success" : True,
                "msg" : "Password reset link sent to email"
            })
        
        except Exception as e:
            print(f"Exception = {e}")
            
            return jsonify({
                "success" : False,
                "msg" : "Failed to send password reset link"
            })
        

@reset_password_bp.route("/account_recovery_page/<token_>")
async def account_recovery_page(token_):

    try:
        token = decode_with_itsdangerous_timed(token_)

        session["token"] = token

        return await render_template(
            "auth_pages/account_recovery_page.html"
        )
    except Exception as e:
    
        return await render_template(
            "auth_pages/token_expired.html"
        )
    


@reset_password_bp.post("/password_reset")
async def password_reset():
    
    async with make_session() as sess:  
        
        form = await request.form

        password = form.get("password", "")
        password_confirm = form.get("password_confirm", "")

        if password != password_confirm:
            return jsonify({
                "success" : False,
                "msg" : "Passwords do not match"
            })
        
        password_hash = await password_maker(password=password)

        try:
            user = await sess.scalar(
                select(UserTable)
                .where(
                    UserTable.id == int(session.get("token", ""))
                )
            )
            
            if user is None:
                return jsonify({
                    "success" : False,
                    "msg" : "Invalid token"
                })
            
            user.password_hash = password_hash

            await sess.commit()

            link_to_login = url_for("timezone_bp.sign_up_page")

            return jsonify({
                "success" : True,
                "msg" : f"password reset successfully",
                "link" : link_to_login
            })
        
        except Exception as e:
            
            print(f"Exception = {e}")
            
            await sess.rollback()
            
            return jsonify({
                "success" : False,
                "msg" : "Failed to reset password"
            })