

from quart import (
    Blueprint,
    jsonify
)

from quart_auth import current_user

from app_db_models.user_model import UserTable

from helper_tools.authenticated_clients_manager import (
    login_required
)
from helper_tools.db_helper import make_session



recover_account_bp = Blueprint("recover_account_bp", __name__)



@recover_account_bp.get("/recover_account")
@login_required
async def recover_account():

    async with make_session() as sess:
        
        if current_user.auth_id:
            user = await sess.get(UserTable, int(current_user.auth_id)) 

            try:
                if user:
                    user.is_account_scheduled_for_deletion = False
                    user.account_scheduled_for_deletion_datetime = None

                    await sess.commit()

                    print(f"recoverd account")

                    return jsonify({
                        "success" : True,
                        "message" : "recoverd account"
                    })
                else:
                    return jsonify({
                            "success" : False,
                            "message" : "user account does not exist"
                        })
                
            except Exception as e:

                print(f"Error recovering account = {e}")

                return jsonify({
                    "success" : False,
                    "message" : "An Error occurred"
                })

        else:
            return jsonify({
                "success" : False,
                "message" : "user account does not exist"
            })