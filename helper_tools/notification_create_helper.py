

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time

from app_db_models.notification_model import NotificationTable


async def create_notification(
        msg:str, link:str, user_id:int, unread:bool=True
) -> None:
    
    async with make_session() as sess:

        try:
            notification = NotificationTable(
                msg=msg,
                link=link,
                created_time=await get_current_time(),
                unread=unread,
                user_id=user_id
            )

            sess.add(notification)
            await sess.commit()

            print("Notification created successfully.")

            return
        except Exception as e:
            print(f"Exception = {e}")
            await sess.rollback()