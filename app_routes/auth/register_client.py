
from quart import (
    Blueprint, request, session, jsonify, url_for
)


from app_db_models.user_model import UserTable
from app_db_models.skill_set_model import SkillSetTable
from app_db_models.refferals_model import ReferralsTable

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time
from helper_tools.web_security import (
    password_maker, encode_with_itsdangerous_timed,
    decode_with_itsdangerous
)
from helper_tools.email_handling.email_sending import send_email_link
from helper_tools.notification_create_helper import create_notification

from sqlalchemy import select

import bleach

import asyncio

import os

from dotenv import load_dotenv
load_dotenv(override=True)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()


register_client_bp = Blueprint("register_client_bp", __name__)


@register_client_bp.post("/auth/register")
async def register_client():
    
    """Register a new client."""

    form = await request.form
    email = bleach.clean(
        str(form.get("email"))
    )
    password = form.get("password")

    refferal_id = session.get("refferal_id")
    if refferal_id:
        try:
            refferal_id_decoded = decode_with_itsdangerous(refferal_id)
            print(f"refferal_id_decoded ")
        except Exception as e:
            print(f"Error decoding refferal_id = {e}")
            refferal_id_decoded = None
    else:
        refferal_id_decoded=None
    

    hashed_password = await password_maker(password=password)

     # Get skill_set - handles both single value and comma-separated multi-select
    skill_set_raw = form.get("skill_set", "").strip()


    if not email or not password:

        return {"message": "Please provide email and password."}
    
    async with make_session() as sess:

        user = await sess.scalar(
            select(UserTable)
            .where(UserTable.email == email)
        )

        if user:

            return {"message": "User already exists."}
        try:

            if email == ADMIN_EMAIL and password == ADMIN_TOKEN:
                account_type = "admin"
                account_status = "active"
                msg="Account created successfully"
            else:
                account_type = form.get("account_type", "").strip()
                account_status="inactive"
                msg="Account activation link sent to your email, expires in 5mins"

            new_user = UserTable(
                email=email,
                password_hash=hashed_password,
                account_class= "premium",
                account_status=account_status,
                account_type=account_type, #client, technician, admin
                account_created_datetime=await get_current_time(),
                user_name =  email.split("@")[0],
                time_zone = session.get("zone_name", "")
            )

            sess.add(new_user)
            await sess.commit()

            user_id = encode_with_itsdangerous_timed(new_user.id)
            
            if refferal_id_decoded:
                try:
                    sess.add(
                        ReferralsTable(
                            referred_user_id=new_user.id,
                            date_time=await get_current_time(),
                            reffered_client_email = email,
                            user_id=int(refferal_id_decoded) #refferal initiator
                        )
                    )

                    reffered_user_name = email.split("@")[0]
                    msg1=f"User {reffered_user_name} registered with your refferal link."
                    msg2="You will receive 1 percent of connects they purchase" 

                    await sess.commit()
                    print("Referral added successfully")

                    await create_notification(
                        msg=msg1+msg2,
                        link="#",
                        unread=True,
                        user_id=int(refferal_id_decoded)
                    )

                    refferal_email = await sess.get(UserTable, int(refferal_id_decoded))
                    
                    if refferal_email:

                        asyncio.create_task(
                            send_email_link(
                                email=refferal_email.email,
                                reason="notification_email",
                                user_name=new_user.user_name,
                                link=url_for(
                                    "dashboard_bp.dashboard",
                                    _external=True
                                )
                            )
                        )

                except Exception as e:
                    await sess.rollback()
                    print(f"Error adding referral = {e}")
                
            
            if new_user.account_type != "admin":

                asyncio.create_task(
                    send_email_link(
                        email=email,
                        reason="activate_account",
                        link=url_for(
                            "activate_account_bp.activate_account",
                            user_id_=user_id,
                            _external=True
                        )
                    )
                )

            #await send_email

            if new_user.account_type == "technician":
                
                try:
                    skill_set_raw = skill_set_raw.split(",")

                    current_time = await get_current_time()

                    sess.add_all([
                        SkillSetTable(
                        skill_set=str(skill_set).capitalize(),
                        user_id=new_user.id,
                        date_time=current_time
                        )
                        for skill_set in skill_set_raw
                    ])
                    
                    await sess.commit()

                except Exception as e:
                    
                    await sess.rollback()
                    print(f"Error = {e}")

            print("User created successfully")

            return jsonify({
                "success":  True,
                "message": msg
            })
        
        except Exception as e:

            print(f"Exception = {e}")

            await sess.rollback()
            return jsonify({
                "success" : False,
                "message" : f"Failed to create account."
            })