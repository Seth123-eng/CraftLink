

from helper_tools.make_sio_server import sio_server

from quart import Blueprint


from app_db_models.chats_model import ChatsTable
from app_db_models.user_model import UserTable


from sqlalchemy import select, or_

from helper_tools.db_helper import make_session
from helper_tools.connects_management import deduct_connects
from helper_tools.date_helper import get_current_time


private_chat_client_bp = Blueprint("private_chat_client_bp", __name__, url_prefix="/private_chats/client")


@sio_server.event
async def join_room(sid, data):

    print(f"join_room data = {data}")

    receiver_id = int(data.get("receiver_id"))
    sender_id = int(data.get("sender_id"))

        
    async with make_session() as sess:

        try:
            receiver = await sess.get(UserTable, int(data.get("receiver_id")))
            sender = await sess.get(UserTable, int(data.get("sender_id")))

            
            if receiver and sender:

                user_ids=sorted([receiver_id, sender_id])
                user_names = sorted([receiver.user_name, sender.user_name])

                room_name = f"{user_ids[0]}_{user_ids[1]}_{user_names[0]}_{user_names[1]}"


                unread_msgs_ = await sess.scalars(
                    select(ChatsTable)
                    .where(
                        ChatsTable.room == room_name,
                        ChatsTable.receiver_id == sender_id,
                        ChatsTable.is_seen == False
                    )
                )
    
                unread_msgs = unread_msgs_.all()

                print(f"unread_msgs={unread_msgs}")
    
                for msg in unread_msgs:
    
                    if msg.sender_id != sender_id:
    
                        msg.is_seen = True
                try:
                    await sess.commit()
                except:
                    await sess.rollback()

                await sio_server.enter_room(
                    sid=sid, room=room_name
                )

                print(f"room_name={room_name}")

                await sio_server.save_session(
                    sid=sid,
                    session={
                        "receiver_id": receiver_id,
                        "sender_id": sender_id,
                        "room_name": room_name
                    }
                )
            else:
                return
            
            chats_ = await sess.scalars(
                select(ChatsTable)
                .where(
                    ChatsTable.room == room_name,
                    or_(
                        ChatsTable.chat_cleared_by != sender_id, #sender is as good as the current user
                        ChatsTable.chat_cleared_by.is_(None)
                    )
                ).order_by(ChatsTable.date_time.asc())
            )

            chats = [
                {
                    "receiver_id" : chat.receiver_id,
                    "sender_id" : chat.sender_id,
                    "message" : chat.message,
                    "is_seen" : chat.is_seen,
                    "receiver_name" : receiver.user_name,
                    "time" : chat.date_time
                }
                for chat in chats_.all()
            ]

            print(f"chats = {chats}")

        except Exception as e:
            print(f"Exception = {e}")
            
            chats = []

        if chats:

            for chat in chats:
                await sio_server.emit(
                    event="receive_message",
                    data={
                        "message": chat.get("message"),
                        "sender_id": chat.get("sender_id"),
                        "receiver_id": chat.get("receiver_id"),
                        "receiver_name" : chat.get("user_name"),
                        "time" : chat.get("time", "").isoformat()
                    },
                    to=sid
                    #skip_sid=sid
                )




@sio_server.event
async def send_message(sid, data):

    client_session = await sio_server.get_session(sid=sid)

    sender_id = int(client_session.get("sender_id"))
    receiver_id = int(client_session.get("receiver_id"))

    print(f"client_session = {client_session}")

    message = data.get("message")

    time = await get_current_time()


    async with make_session() as sess:

        try:

            connect_deduction_result = await deduct_connects(
                user_id=sender_id
            )

            if connect_deduction_result.get("success") == True:
                await sio_server.emit(
                    event="receive_message",
                    data={
                        "message": message,
                        "sender_id": sender_id,
                        "receiver_id": receiver_id,
                        "time" : time.isoformat()
                    },
                    to=client_session.get("room_name")
                )


                new_msg = ChatsTable(
                    receiver_id=receiver_id,
                    sender_id=sender_id,
                    message=message,
                    room = client_session.get("room_name"),
                    chat_cleared_by=None,
                    is_seen=False,
                    date_time=await get_current_time()
                )

                sess.add(new_msg)
                await sess.commit()
            else:
                print(f"Connect deduction failed: {connect_deduction_result.get('message')}")
        except Exception as e:
            print(f"Exception = {e}")

            await sess.rollback()



@sio_server.event
async def clear_chats(sid):
        
    async with make_session() as sess:
        
        sio_session = await sio_server.get_session(sid=sid)

        room_name = sio_session.get("room_name")
        
        try:

            if room_name:

                chats_ = await sess.scalars(
                    select(ChatsTable)
                    .where(
                        ChatsTable.room == room_name
                    )
                )

                for chat in chats_.all():

                    if chat.chat_cleared_by is not None:
                        await sess.delete(chat)

                    chat.chat_cleared_by = int(sio_session.get("sender_id"))

                await sess.commit()

                msgs = []

                for msg in msgs:

                    await sio_server.emit(
                        event="receive_message",
                        data={
                            "message": msg.get("message"),
                            "sender_id": msg.get("sender_id"),
                            "receiver_id": msg.get("receiver_id"),
                            "receiver_name" : msg.get("user_name"),
                            "time" : msg.get("time", "").isoformat()
                        },
                        to=sid
                        #skip_sid=sid
                    )

        except Exception as e:
            print(f"Exception = {e}")

            await sess.rollback()