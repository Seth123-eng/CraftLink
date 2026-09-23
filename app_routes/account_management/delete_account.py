

from quart import (
    Blueprint, jsonify
)

from quart_auth import current_user

from app_db_models.user_model import UserTable

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time
from helper_tools.authenticated_clients_manager import login_required


from sqlalchemy import select


delete_account_bp = Blueprint("delete_account_bp", __name__)


@delete_account_bp.get("/delete/account")
@login_required
async def delete_account():
        
        
    async with make_session() as sess:
        
        if current_user.auth_id is not None:

            user = await sess.scalar(
                select(UserTable)
                .where(UserTable.id == int(current_user.auth_id))
            )
        
        if not user:
            
            return jsonify({
                "success" : False,
                "message" : f"User does not exist,"
            })
        
        try:

            user.is_account_scheduled_for_deletion = True
            user.account_scheduled_for_deletion_datetime = await get_current_time()

            await sess.commit()

            print(f"client deleted!!")

            return jsonify({
                "success" : False,
                "message" : f"Account scheduled for deletion"
            })

        except Exception as e:

            print(f"Error = {e}")

            await sess.rollback()

            return jsonify({
                "success" : False,
                "message" : f"An Error Occurred... try again later"
            })