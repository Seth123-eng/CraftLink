

from quart import (
    Blueprint, request, jsonify
)

from quart_auth import current_user


from app_db_models.complaints_report_model import ComplaintsTable

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time
from helper_tools.authenticated_clients_manager import login_required
from helper_tools.web_security import (
    decode_with_itsdangerous
)


complaints_reporting_bp = Blueprint("complaints_reporting_bp", __name__)


@complaints_reporting_bp.post("/complaints_reporting")
@login_required
async def complaints_reporting():

    async with make_session() as sess:

        form = await request.form
        
        try:
            new_complaint = ComplaintsTable(
                complaint_type=form.get("complaint_type"),
                complaint_info=form.get("complaint_info"),
                complained_to=decode_with_itsdangerous(
                    form.get("other_user_id"),
                ),
                user_id=int(current_user.auth_id) if current_user.auth_id is not None else None,
                date_time=await get_current_time()
            )

            sess.add(new_complaint)

            await sess.commit()

            return jsonify({
                "success" : True,
                "msg" : "Complaint submitted successfully"
            })
        
        except Exception as e:

            print(f"Exception = {e}")

            return jsonify({
                "success" : False,
                "msg" : "An Error occurred, try again"
            })