

from quart import (
    Blueprint, render_template, jsonify
)

from quart_auth import current_user

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    admin_required
)
from helper_tools.web_security import (
    encode_with_itsdangerous, decode_with_itsdangerous
)

from app_db_models.complaints_report_model import ComplaintsTable
from app_db_models.user_model import UserTable


from sqlalchemy import select


complaints_bp = Blueprint('complaints_bp', __name__)


@complaints_bp.get("/complaints_page")
@admin_required
async def complaints_page():
    
    return await render_template(
        "admin/complaints.html"
    )


@complaints_bp.get("/get/complaints")
@admin_required
async def get_complaints():

    async with make_session() as session:

        try:
            complaints_ = await session.execute(
                select(ComplaintsTable)
            )

            complaints = [
                {
                    "id": encode_with_itsdangerous(complaint.id),
                    "complaint_type": complaint.complaint_type,
                    "complaint_info": complaint.complaint_info,
                    "complained_to": complaint.complained_to,
                    "date_time": complaint.date_time,
                    "is_read": complaint.is_read,
                    "user_id": complaint.user_id #client filling complaint
                }
                for complaint in complaints_.scalars().all()
            ]
        except Exception as e:
            print(f"Exception = {e}")
            complaints=[]

        if complaints:

            return jsonify({
                "success": True,
                "complaints": complaints
            })
        else:
            return jsonify({
                "success": False,
                "complaints": []
            })
        



@complaints_bp.get("/mark/complaints/read/<complaint_id_>")
@admin_required
async def mark_complaints_read(complaint_id_):
    
    async with make_session() as sess:

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        
        else:

            try:

                complaint_id = decode_with_itsdangerous(complaint_id_)

                complaint = await sess.scalar(
                    select(ComplaintsTable)
                    .where(
                        ComplaintsTable.id == complaint_id
                    )
                )
                
                if complaint:
                    complaint.is_read = True

                    await sess.commit()

                return jsonify({
                    "success": True,
                    "msg": "Complaint marked as read successfully"
                })
            
            except Exception as e:
                
                print(f"Exception = {e}")
                
                await sess.rollback()
                
                return jsonify({
                    "success": False,
                    "msg": "Complaint not marked as read"
                })
            

@complaints_bp.get("/remove/complaint/<complaint_id_>")
@admin_required
async def remove_complaint(complaint_id_):

    async with make_session() as sess:

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        
        else:

            try:

                complaint_id = decode_with_itsdangerous(complaint_id_)

                complaint = await sess.scalar(
                    select(ComplaintsTable)
                    .where(
                        ComplaintsTable.id == complaint_id
                    )
                )

                await sess.delete(complaint)

                await sess.commit()

                return jsonify({
                    "success": True,
                    "msg": "Complaint marked as read successfully"
                })
            
            except Exception as e:
                
                print(f"Exception = {e}")
                
                await sess.rollback()
                
                return jsonify({
                    "success": False,
                    "msg": "Complaint not marked as read"
                })