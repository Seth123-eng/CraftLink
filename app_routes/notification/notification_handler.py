

from quart import (
    Blueprint, render_template, jsonify
)

from quart_auth import current_user

from app_db_models.notification_model import NotificationTable

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    login_required
)
from helper_tools.web_security import (
    encode_with_itsdangerous, decode_with_itsdangerous
)

from sqlalchemy import select


notification_bp = Blueprint("notification_bp", __name__)


@notification_bp.get("/notification/page")
@login_required
async def notification_page():

    return await render_template("notifications.html")


@notification_bp.get("/notification/fetch")
@login_required
async def fetch_notifications():

    if current_user.auth_id is None:

        return jsonify({
            "success": False,
            "message": "User not authenticated"
        })

    async with make_session() as sess:

        notifications = await sess.scalars(
            select(NotificationTable)
            .where(
                NotificationTable.user_id == int(current_user.auth_id),
            )
        )

        notifications_list = [
            {
                "id": encode_with_itsdangerous(notification.id),
                "unread": notification.unread,
                "link": notification.link,
                "message": notification.msg,
                "created_time": notification.created_time.isoformat() if notification.created_time else None
            }
            for notification in notifications.all()
        ]

        if notifications_list:

            return {
                "success": True,
                "notifications": notifications_list
            }
        else:
            return jsonify({
                "success": False,
                "notifications": []
            })
        


@notification_bp.get("/notification/delete/<notification_id_>")
@login_required
async def delete_notification(notification_id_):
    
    if current_user.auth_id is None:
        return jsonify({
            "success": False,
            "message": "User not authenticated"
        })
    
    async with make_session() as sess:
        
        try:
            notification_id = decode_with_itsdangerous(notification_id_)

            if not notification_id:
                return jsonify({
                    "success": False,
                    "msg": "Notification not Found."
                })

            notification = await sess.scalar(
                select(NotificationTable)
                .where(
                    NotificationTable.id == int(notification_id),
                    NotificationTable.user_id == int(current_user.auth_id)
                )
            )
            
            await sess.delete(notification)
            await sess.commit()
            
            return jsonify({
                "success": True,
                "message": "Notification deleted successfully"
            })
        
        except Exception as e:
            print(f"Exception = {e}")
            
            return jsonify({
                "success": False,
                "message": "Failed to delete notification"
            })
        

@notification_bp.post("/notification/mark-as-read/<notification_id>")
@login_required
async def mark_all_notifications_read(notification_id):
    
    if current_user.auth_id is None:
        return jsonify({
            "success": False,
            "message": "User not authenticated"
        })
    
    async with make_session() as sess:

        try:
            notification_id = decode_with_itsdangerous(notification_id)

            if not notification_id:
                return jsonify({
                    "success": False,
                    "msg": "Notification not Found."
                })

            notification = await sess.scalar(
                select(NotificationTable)
                .where(
                    NotificationTable.id == int(notification_id),
                    NotificationTable.user_id == int(current_user.auth_id)
                )
            )
            if notification:
                notification.unread = False
                await sess.commit()

                return jsonify({
                    "success": True,
                    "message": "Notification marked as read successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Notification not found"
                })
        except Exception as e:
            print(f"Exception = {e}")

            await sess.rollback()
            
            return jsonify({
                "success": False,
                "message": "Failed to mark notification as read"
            })