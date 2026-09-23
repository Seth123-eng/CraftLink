

from app_db_models.connects_model import ConnectsTable
from app_db_models.refferals_model import ReferralsTable
from app_db_models.user_model import UserTable

from quart_auth import current_user

from helper_tools.date_helper import get_current_time
from helper_tools.db_helper import make_session

from sqlalchemy import select



async def award_connects(connects_purchased:float) ->None:

    async with make_session() as sess:

        if current_user.auth_id is None:

            print(f"You must be logged in!!")
            return
        
        admin = await sess.scalar(
            select(UserTable)
            .where(
                UserTable.id == int(current_user.auth_id),
                UserTable.account_type == "admin"
            ))

        if admin:
            print("Admin not allowed here")
            return

        user_reffered_by = await sess.scalar(
            select(ReferralsTable)
            .where(
                ReferralsTable.referred_user_id == int(current_user.auth_id)
            )
        )

        if not user_reffered_by:
            print(f"No refferals found")
            return
        
        award_connects = ((1/100)*connects_purchased)

        refferal_initiated_by = await sess.scalar(
            select(ConnectsTable)
            .where(
                ConnectsTable.user_id == int(user_reffered_by.user_id)
            )
        )


        if not refferal_initiated_by:
            print(f"No refferals found")
            
            try:
                sess.add(
                    ConnectsTable(
                        user_id = user_reffered_by.user_id,
                        available_connects = award_connects,
                        connects_from_referral = award_connects,
                        date_time = await get_current_time()
                    )
                )

                await sess.commit()
                print(f"registered new connects")

            except Exception as e:
                print(f"Error = {e}")
                await sess.rollback()
        else:

            try:
                refferal_initiated_by.available_connects += award_connects
                refferal_initiated_by.connects_from_referral += award_connects
    
                await sess.commit()
            except Exception as e:
                print(f"Error = {e}")
                await sess.rollback()
