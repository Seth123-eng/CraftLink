

from quart import (
    Blueprint, request, url_for, redirect,
    jsonify, render_template, session
)

from quart_auth import current_user

from app_db_models.refferals_model import ReferralsTable
from app_db_models.connects_model import ConnectsTable
from app_db_models.user_model import UserTable

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    login_required
)
from helper_tools.date_helper import get_current_time
from helper_tools.web_security import (
    encode_with_itsdangerous, decode_with_itsdangerous
)

from helper_tools.email_handling.email_sending import send_email_link

from sqlalchemy import select, func

import bleach

import asyncio


refferals_bp = Blueprint("refferals_bp", __name__)


@refferals_bp.get("/refferals_page")
@login_required
async def refferals_page():

    try:
        uid_ = encode_with_itsdangerous(current_user.auth_id)

        refferal_link = url_for(
            "refferals_bp.load_reffered_client",
            uid_=uid_,
            client_id_=uid_,
            _external=True
        )
    except Exception as e:
        print(f"Error: {e}")
        refferal_link = ""
    
    return await render_template("refferals_page.html",
                                 refferal_link=refferal_link)


@refferals_bp.get("/connects_awarded_from/referrals")
@login_required
async def connects_awarded_from_referrals():

    async with make_session() as sess:
        
        try:
            if not current_user.auth_id:

                return jsonify({
                    "success": False,
                    "message": "You must be logged in to view referrals"
                })
            
            connects_from_refferals = await sess.scalar(
                select(ConnectsTable)
                .where(
                    ConnectsTable.user_id == int(current_user.auth_id)
                )
            )

            print(f"connects_from_refferals = {connects_from_refferals}")

            if connects_from_refferals is None:
                print(f"User not found")

                return jsonify({
                    "success": False,
                    "message": 0
                })
            
            else:
                return jsonify({
                    "success": True,
                    "connects_from_refferals": connects_from_refferals.connects_from_referral
                })
        
        except Exception as e:
            print(f"Error: {e}")

            return jsonify({
                    "success": False,
                    "message": 0
                })



@refferals_bp.get("/account/referrals")
@login_required
async def account_referrals():
    
    async with make_session() as sess:
        
        try:

            if not current_user.auth_id:
                return jsonify({
                    "success": False,
                    "message": "You must be logged in to view referrals"
                })
            
            referrals = await sess.scalar(
                select(func.count(ReferralsTable.id))
                .where(
                    ReferralsTable.user_id == int(current_user.auth_id)
                )
            )
            print(f"referrals = {referrals}")
            
            if not referrals:
                print(f"User not found")

                return jsonify({
                    "success": False,
                    "message": 0
                })
            
            else:
                return jsonify({
                    "success": True,
                    "referrals": referrals
                })
        
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({
                "success": False,
                "message": "Error Loading refferals"
            })
        


@refferals_bp.get("/reffered/clients")
@login_required
async def reffered_clients():

    async with make_session() as sess:

        if not current_user.auth_id:
            return jsonify({
                "success": False,
                "message": "You must be logged in"
            })

        reffered_clients_ = await sess.execute(
            select(ReferralsTable)
            .where(
                ReferralsTable.user_id == int(current_user.auth_id)
            )
        )

        reffered_clients = [
            {
                "id": encode_with_itsdangerous(refferal.id),
                "email" : refferal.reffered_client_email,
                "date_time": refferal.date_time.isoformat() if refferal.date_time else None
            }
            for refferal in reffered_clients_.scalars().all()
        ]

        if reffered_clients:
            return jsonify({
                "success" : True,
                "reffered_clients" : reffered_clients
            })
        return jsonify({
            "success" : False,
            "message" : "No referrals found"
        })



@refferals_bp.post("/send_refferal/link")
@login_required
async def send_refferal_link():

    form = await request.form

    email = bleach.clean(
        form.get("email", "").strip()
    )

    if current_user.auth_id is None:

        return jsonify({
            "success": False,
            "message": "You must be logged in to send a referral link"
        })

    uid_ = encode_with_itsdangerous(current_user.auth_id)

    link = url_for(
        "refferals_bp.load_reffered_client",
        uid_=uid_,
        client_id_=uid_,
        _external=True
    )

    try:

        asyncio.create_task(
            send_email_link(
                email=email,
                link=link,
                reason="send_refferal_link",
            )
        )

        return jsonify({
            "success": True,
            "message": "Email sent"
        })
    except Exception as e:

        print(f"Error sending email: {e}")

        return jsonify({
            "success": False,
            "message": "Error sending email"
        })



@refferals_bp.get("/load_reffered/client/<uid_>/<client_id_>")
async def load_reffered_client(uid_, client_id_):

    session["refferal_id"] = client_id_

    return redirect(url_for("timezone_bp.sign_up_page"))