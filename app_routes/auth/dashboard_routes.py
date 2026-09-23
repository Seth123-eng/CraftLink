
from quart import render_template, Blueprint, jsonify

from quart_auth import current_user

from helper_tools.authenticated_clients_manager import (
    login_required, get_current_user
)
from helper_tools.db_helper import make_session

from app_db_models.connects_model import ConnectsTable
from app_db_models.payment_info_model import TotalPaymentsTable
from app_db_models.chats_model import ChatsTable
from app_db_models.notification_model import NotificationTable

from sqlalchemy import select, func


dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.get("/dashboard")
@login_required
async def dashboard():

    current_user_ = await get_current_user()

    
    return await render_template(
        "auth_pages/dashboard/dashboard.html",
        current_user_=current_user_
    )


@dashboard_bp.get("/dashboard/overview")
@login_required
async def dashboard_overview():

    current_user_ = await get_current_user()
    
    return await render_template(
        "auth_pages/dashboard/dashboard_overview.html",
        current_user_=current_user_
    )


@dashboard_bp.get("/dashboard/available-connects")
@login_required
async def dashboard_available_connects():
    
    async with make_session() as sess:

        if current_user.auth_id:
        
            connects = await sess.scalar(
                select(ConnectsTable)
                .where(
                    ConnectsTable.user_id == int(current_user.auth_id)
                )
            )

            if connects:

                return jsonify({
                    "success": True,
                    "connects": connects
                })
            else:
                return jsonify({
                    "success": False,
                    "connects": "No connects found"
                })
            
        else:
            return jsonify({
                "success": False,
                "connects": "User not authenticated"
            })
        



@dashboard_bp.route("/dashboard/total-payments", methods=["GET"])
@login_required
async def dashboard_total_payments():
    
    async with make_session() as sess:

        if current_user.auth_id:
            
            payments = await sess.scalar(
                select(TotalPaymentsTable)
                .where(
                    TotalPaymentsTable.user_id == int(current_user.auth_id),
                    TotalPaymentsTable.is_received == True
                )
            )

            total_received = payments.amount if payments else 0.00

            if total_received:

                return jsonify({
                    "success" : True,
                    "total_received" : total_received
                })
            
            else:
                return jsonify({
                    "success" : False,
                    "total_received" : "No payments found"
                })

        else:
            return jsonify({
                "success" : False,
                "total_received" : "User not authenticated"
            })
        

@dashboard_bp.get("/dashboard/unread_chats/total")
@login_required
async def dashboard_unread_chats_total():
    
    async with make_session() as sess:

        if current_user.auth_id:
            
            total_unread = await sess.scalar(
                select(func.count(func.distinct(ChatsTable.room)))
                .where(
                    ChatsTable.receiver_id == int(current_user.auth_id),
                    ChatsTable.is_seen == False
                )
            )

            if total_unread:

                return jsonify({
                    "success" : True,
                    "total_unread" : total_unread
                })
            
            else:
                return jsonify({
                    "success" : False,
                    "total_unread" : 0
                })

        else:
            return jsonify({
                "success" : False,
                "total_unread" : "User not authenticated"
            })
        

@dashboard_bp.get("/total_new/notifications")
@login_required
async def dashboard_total_new_notifications():
    
    async with make_session() as sess:

        if current_user.auth_id:
            
            total_new = await sess.scalar(
                select(func.count(NotificationTable.id))
                .where(
                    NotificationTable.user_id == int(current_user.auth_id),
                    NotificationTable.unread == True
                )
            )

            print(f"total_new = {total_new}")
            
            if total_new:

                return jsonify({
                    "success" : True,
                    "total_new" : total_new
                })
            
            else:
                return jsonify({
                    "success" : False,
                    "total_new" : 0
                })

        else:
            return jsonify({
                "success" : False,
                "total_new" : "User not authenticated"
            })