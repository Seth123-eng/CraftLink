

from helper_tools.db_helper import make_session

from app_db_models.connects_model import ConnectsTable

from sqlalchemy import select




async def deduct_connects(user_id:int) -> dict:

    if user_id is not None:

        async with make_session() as sess:

            user_connects = await sess.scalar(
                select(ConnectsTable)
                .where(ConnectsTable.user_id == user_id)
            )

            if not user_connects:
                return {
                    "success": False,
                    "message": "User does not exist"
                }
            
            try:

                if user_connects.available_connects > 0:
                    user_connects.available_connects -= 1
                    await sess.commit()
                    return {
                        "success": True,
                        "message" : "Connect deducted successfully"
                    }
                
                else:
                    return {
                        "success": False,
                        "message": "No connects available to deduct"
                    }

            except Exception as e:
                print(f"Error = {e}")
                await sess.rollback()
                return {
                    "success": False,
                    "message": "Error occurred while deducting connect"
                }

    else:
        return {
            "success": False,
            "message": "user does not exist"
        }