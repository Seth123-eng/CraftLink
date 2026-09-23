

from quart import (
    Blueprint, render_template, session, url_for, jsonify,
    redirect, request
)

from quart_auth import current_user

from helper_tools.authenticated_clients_manager import (
    login_required
)
from helper_tools.db_helper import make_session
from helper_tools.web_security import (
    encode_with_itsdangerous, decode_with_itsdangerous
)

from app_db_models.user_model import UserTable
from app_db_models.chats_model import ChatsTable
from app_db_models.connects_model import ConnectsTable

from sqlalchemy import select, or_
from sqlalchemy.orm import aliased



private_chat_bp = Blueprint("private_chat_bp", __name__, url_prefix="/private_chats")


@private_chat_bp.get("/my-chats/page")
@login_required
async def my_chats():
    
    return await render_template(
        "private_chat/my_chats.html"
    )


@private_chat_bp.get("/get_receiver_id")
@login_required
async def get_receiver_id():

    data = decode_with_itsdangerous(
        request.args.get("receiver_id")
    )

    print(f"data = {data}")

    receiver_id = str(data).split("=")[-1]

    print(f"receiver_id = {receiver_id}")

    if receiver_id:

        async with make_session() as sess:
            receiver = await sess.get(UserTable, int(receiver_id))
            
            if receiver:
                receiver_name = receiver.user_name
        
                session["receiver_name"] = receiver_name
                session["receiver_id"] = receiver_id
            else:
                return jsonify({
                    "success" : False,
                    "redirect" : "Unable to locate the receiver in the records"
                })
        
    return redirect(url_for("private_chat_bp.private_chat_page"))




@private_chat_bp.get("/my-chats/history")
@login_required
async def my_chats_history():
    
    async with make_session() as sess:
        
        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        
        # Use aliases for the UserTable to avoid ambiguity
        sender_alias = aliased(UserTable)
        receiver_alias = aliased(UserTable)

        # Get all chats where current user is either sender or receiver
        chats_ = await sess.execute(
            select(
                ChatsTable,
                sender_alias,
                receiver_alias
            )
            .join(sender_alias, ChatsTable.sender_id == sender_alias.id)
            .join(receiver_alias, ChatsTable.receiver_id == receiver_alias.id)
            .where(
                or_(
                    ChatsTable.sender_id == int(current_user.auth_id),
                    ChatsTable.receiver_id == int(current_user.auth_id)
                )
            )
            .order_by(ChatsTable.date_time.desc())
        )

        chat_partners = {}
        
        for chat, sender_user, receiver_user in chats_.all():
            # Determine the other person and if the current user has unread messages from them
            if chat.sender_id == int(current_user.auth_id):
                # Current user sent the message, so they've seen it
                partner_id = encode_with_itsdangerous(chat.receiver_id)
                partner_name = receiver_user.user_name
                partner_avatar = getattr(receiver_user, 'avatar_url', "")
                # For messages sent by current user, is_seen is True (they already saw it)
                is_unread = False
            else:
                # Other person sent the message to current user
                partner_id = encode_with_itsdangerous(chat.sender_id)
                partner_name = sender_user.user_name
                partner_avatar = getattr(sender_user, 'avatar_url', "")
                # Check if the message is unread by the current user
                is_unread = not chat.is_seen
            
            # Only show unread status if the most recent message was sent by the other person
            if partner_id not in chat_partners:
                chat_partners[partner_id] = {
                    "receiver_id": partner_id,
                    "user_name": partner_name,
                    "avatar_url": partner_avatar,
                    "last_message_time": chat.date_time.isoformat() if chat.date_time else None,
                    "is_seen": not is_unread,  # is_seen is True if message has been read by current user
                    "last_message_sender": chat.sender_id
                }
            elif not chat.is_seen and chat.sender_id != int(current_user.auth_id):
                # If this is a newer unread message from the other person, update unread status
                chat_partners[partner_id]["is_seen"] = False

        chats = list(chat_partners.values())

        if chats:
            return jsonify({
                "success": True,
                "chats": chats
            })
        else:
            return jsonify({
                "success": False,
                "chats": []
            })


@private_chat_bp.route("/private_chat/page", methods=["GET"])
@login_required
async def private_chat_page():


    sender_id = current_user.auth_id if await current_user.is_authenticated else None
    receiver_id = session.get("receiver_id")
    receiver_name = session.get("receiver_name")


    async with make_session() as sess:
        
        if current_user.auth_id is None:

            return await render_template(
                "auth_pages/sign_up_login_page.html"
            )
        
        user_connects = await sess.scalar(
            select(ConnectsTable)
            .where(
                ConnectsTable.user_id == int(current_user.auth_id)
            )
        )

        if user_connects and user_connects.available_connects > 1:
    
            return await render_template(
                "private_chat/private_chat_page.html",
                sender_id=sender_id,
                receiver_id=receiver_id,
                receiver_name=receiver_name,
                # Pass the current user ID directly from the backend
                current_user_id=current_user.auth_id if await current_user.is_authenticated else None
            )
        else:
            return await render_template(
                "by_connects.html"
            )