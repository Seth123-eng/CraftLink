

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time

from app_db_models.connects_model import ConnectsTable

from sqlalchemy import select



async def purchase_connects(purchased_connects:str, user_id:int) -> str|None:
        
    async with make_session() as sess:

        try:

            if user_id is None:

                return "No user found"

            connects = await sess.scalar(
                select(ConnectsTable)
                .where(
                    ConnectsTable.user_id == user_id
                )
            )
            
            if connects:
                connects.available_connects += int(purchased_connects)
                await sess.commit()

            else:
                sess.add(ConnectsTable(
                    user_id=user_id,
                    available_connects=int(purchased_connects),
                    connects_from_referral=0,
                    date_time=await get_current_time()
                ))

                await sess.commit()


            print("connects purchased successfully")

        except Exception as e:

            print("Error purchasing connects")
            
            print(f"Exception = {e}")
            await sess.rollback()