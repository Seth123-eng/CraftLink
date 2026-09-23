

from app_db_models.user_model import UserTable
from app_db_models.job_postings_models import JobPostingsTable
from app_db_models.payment_info_model import TotalPaymentsTable

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    admin_required
)

from quart_auth import current_user

from sqlalchemy import select, func

from quart import (
    Blueprint, jsonify
)


dashboard_items_bp = Blueprint("dashboard_items_bp", __name__)


@dashboard_items_bp.get("/total_users")
@admin_required
async def total_users():
    
    async with make_session() as sess:

        user_count = await sess.scalar(
            select(func.count(UserTable.id))
        )

        if user_count is None:
            return jsonify({
                "success": False,
                "message": "Error counting users"
            })
        
        return jsonify({
            "success": True,
            "total_users": int(user_count)
        })
    


@dashboard_items_bp.get("/total_job_posts")
@admin_required
async def total_job_posts():
    
    async with make_session() as sess:

        job_postings_count = await sess.scalar(
            select(func.count(JobPostingsTable.id))
        )

        if job_postings_count is None:
            return jsonify({
                "success": False,
                "message": "Error counting job postings"
            })
        
        return jsonify({
            "success": True,
            "total_job_posts": int(job_postings_count)
        })
    


@dashboard_items_bp.get("/total_revenue")
@admin_required
async def total_revenue():

    async with make_session() as sess:

        if current_user.auth_id is None:

            return jsonify({
                "success" : False,
                "message" : "You are not logged in"
            })
        
        total_revenue = await sess.scalar(
            select(TotalPaymentsTable)
            .where(
                TotalPaymentsTable.user_id == int(current_user.auth_id)
            )
        )

        if total_revenue:

            return jsonify({
                "success": True,
                "total_revenue": total_revenue.amount
            })
        else:
            return jsonify({
                "success": False,
                "total_revenue": 0
            })