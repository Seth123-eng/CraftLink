

from quart import (
    Blueprint, request, url_for,
    jsonify, render_template
)

from quart_auth import current_user

from app_db_models.user_model import UserTable
from app_db_models.skill_set_model import SkillSetTable
from app_db_models.file_model import FileTable

from helper_tools.db_helper import make_session
from helper_tools.web_security import password_maker
from helper_tools.authenticated_clients_manager import login_required

from sqlalchemy import select

from app_factory import web_app

import os

from dotenv import load_dotenv
load_dotenv(override=True)

filebase_cdn_base_url = os.getenv("FILEBASE_CDN_BASE_URL", "").strip()


update_account_info_bp = Blueprint("update_account_info_bp", __name__)


@update_account_info_bp.get("/account_management/page")
@login_required
async def account_management_page():

    return await render_template("account_management_page.html")



@update_account_info_bp.route("/user/info", methods=["GET"])
@login_required
async def get_user_info():
    """Get current user information for the account management page."""
    
    if not await current_user.is_authenticated or current_user.auth_id is None:
        return jsonify({
            "success": False,
            "message": "User not authenticated",
            "redirect": url_for("login_logout_bp.handle_logout")
        }), 401
    
    async with make_session() as sess:
        try:
            record = await sess.execute(
                select(FileTable, UserTable)
                .join(UserTable, FileTable.user_id == UserTable.id)
                .where(
                    FileTable.is_profile.is_(True),
                    FileTable.user_id == int(current_user.auth_id)
                )
            )

            result = record.first()
            
            if result:

                avatar, user = result
                
                try:
                    skills = await sess.scalars(
                        select(SkillSetTable)
                        .where(SkillSetTable.user_id == int(current_user.auth_id))
                    )

                    skill_list = [skill.skill_set for skill in skills.all()]
                except Exception as e:
                    print(f"Exception = {e}")
                    skill_list = []
                
                response = {
                    "success": True,
                    "user_name": user.user_name or user.email.split("@")[0],
                    "email": user.email,
                    "is_account_scheduled_for_deletion": user.is_account_scheduled_for_deletion,
                    "account_type": user.account_type or "Member",
                    "account_class": user.account_class or "standard",
                    "time_zone": user.time_zone,
                    "created_at": user.account_created_datetime.isoformat() if user.account_created_datetime else None,
                    "is_account_scheduled_for_deletion": getattr(user, "is_account_scheduled_for_deletion", False),
                    "skills": skill_list,
                    "avatar_url": f"{filebase_cdn_base_url}/{avatar.file_name}" if avatar else None
                }

            else:

                user_ = await sess.get(UserTable, int(current_user.auth_id))

                if user_:

                    response={
                        "success": True,
                        "user_name": user_.user_name or user_.email.split("@")[0],
                        "email": user_.email,
                        "is_account_scheduled_for_deletion": user_.is_account_scheduled_for_deletion,
                        "account_type": user_.account_type,
                        "account_class": user_.account_class,
                        "time_zone": user_.time_zone,
                        "created_at": user_.account_created_datetime.isoformat() if user_.account_created_datetime else None,
                        "is_account_scheduled_for_deletion": user_.is_account_scheduled_for_deletion,
                        "skills": [],
                        "avatar_url": ""
                    }
                else:
                    response={}

            return jsonify(
                response
            )
            
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return jsonify({
                "success": False,
                "message": "Failed to fetch user information"
            }), 500



@update_account_info_bp.route("/update/account_info", methods=["GET", "POST"])
@login_required
async def update_account_info():
    
    if request.method == "POST":
        
        form = await request.form
        
        current_password = form.get("current_password", "")
        new_password = form.get("new_password", "")
        user_name = form.get("user_name", "")

        
        if not current_password or not new_password:
            
            return jsonify({
                "success" : False,
                "message" : f"Please provide current password and new password."
            })
        
        async with make_session() as sess:
            
            if current_user.auth_id is not None:

                user = await sess.scalar(
                    select(UserTable)
                    .where(UserTable.id == int(current_user.auth_id))
                )
            
            if not user:
                
                return jsonify({
                    "success" : False,
                    "message" : f"User does not exist, sign up instead.."
                })
            
            if user.failed_login_attempts >= 5:
                
                return jsonify({
                    "success" : False,
                    "message" : f"Account locked, try again later."
                })
            
            if await web_app.bcrypt.async_check_password_hash(
                password=current_password,
                pw_hash=user.password_hash
            ):
                
                hashed_password = await password_maker(password=new_password.encode("utf-8"))
                
                try:
                    
                    user.password_hash = hashed_password
                    user.user_name = user_name
                    
                    await sess.commit()
                    
                    print("password updated successfully")
                    
                    return jsonify({
                        "success" : True,
                        "message" : f"Password updated successfully"
                    })
                    
                except Exception as e:
                    
                    print(f"Exception = {e}")
                    
                    await sess.rollback()
                    
                    return jsonify({
                        "success" : False,
                        "message" : f"Failed to update password"
                    })
            else:
                
                return jsonify({
                    "success" : False,
                    "message" : f"Invalid current password entered!!"
                })
    else:
        
        return jsonify({
            "redirect": url_for("update_account_info_bp.update_password_page")
        })