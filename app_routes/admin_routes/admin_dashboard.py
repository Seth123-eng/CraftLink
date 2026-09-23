

from quart import (
    Blueprint, render_template, jsonify,
    request
)

from quart_auth import current_user

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    admin_required, login_required
)
from helper_tools.web_security import (
    encode_with_itsdangerous, decode_with_itsdangerous
)

from app_db_models.connects_model import ConnectsManagement
from app_db_models.user_model import UserTable
from app_db_models.payment_info_model import (
    TotalPaymentsTable
)


from sqlalchemy import select

from app_routes.admin_routes.admin_helpers.add_connects_helper import add_connects


admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.get("/admin/overview_page")
@admin_required
async def admin_overview_page():
    
    return await render_template(
        "admin/admin_overview_page.html"
    )


@admin_bp.get("/admin/payments")
@admin_required
async def payments():

    return await render_template(
        "admin/payments.html"
    )


@admin_bp.get("/update/connects/page")
@admin_required
async def update_connects_page():
    
    return await render_template(
        "admin/update_connects.html"
    )



@admin_bp.get("/get/connects")
@login_required
async def get_connects():
    
    async with make_session() as sess:
        
        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        user = await sess.get(UserTable, int(current_user.auth_id))
        
        if user is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        connects_ = await sess.execute(
            select(ConnectsManagement)
        )

        try:

            connects = [
                {
                    "connect_id" : encode_with_itsdangerous(connect.id),
                    "connects": connect.connects,
                    "connects_cost": connect.connects_cost,
                    "date_time": connect.date_time
                }
                for connect in connects_.scalars().all()
            ]

            print(f"connects = {connects}")

        except Exception as e:
            print(f"Error getting connects: {e}")

            return jsonify({
                "success": False,
                "message": "Error getting connects"
            })
        
        return jsonify({
            "success": True,
            "message": "Connects received",
            "connects": connects
        })



#handles both update and initial add of connects
@admin_bp.post("/update/connects")
@admin_required
async def update_connects():

    async with make_session() as sess:

        form = await request.form

        #expected as "connects:cost", i.e "1:100, 2:200"
        connects_with_cost_string = form.get("connects_with_cost", "")

        if connects_with_cost_string.strip() == "":
            return jsonify({
                "success": False,
                "message": "No connects provided"
            })
        
        connects_with_cost = connects_with_cost_string.split(",")

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to update connects"
            })
        
        user = await sess.get(UserTable, int(current_user.auth_id))
        
        if user is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to update connects"
            })
        
        
        try:
            await add_connects(user.id, connects_with_cost)

            return jsonify({
                "success" : True,
                "message" : "Updated connects"
            })

        except Exception as e:

            await sess.rollback()

            print(f"Error Updating connects: {e}")

            return jsonify({
                "success" : False,
                "message" : "Error Updating connects"
            })
        

@admin_bp.get("/remove/connects/<connect_id_>")
@admin_required
async def remove_connects(connect_id_):

    connect_id = decode_with_itsdangerous(connect_id_)
    
    async with make_session() as sess:
        
        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        user = await sess.get(UserTable, int(current_user.auth_id))
        
        if user is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        connects = await sess.scalar(
            select(
                ConnectsManagement
            )
            .where(
                ConnectsManagement.user_id == user.id,
                ConnectsManagement.id == int(connect_id)
            )
        )

        if connects:
            try:
                await sess.delete(connects)
                await sess.commit()

                return jsonify({
                    "success": True,
                    "message": "Connects removed"
                })
            except Exception as e:
                await sess.rollback()
                print(f"Error removing connects: {e}")
                return jsonify({
                    "success": False,
                    "message": "Error removing connects"
                })
            
        else:
            return jsonify({
                "success" : False,
                "message" : "Connect does not exist"
            })
            

@admin_bp.get("/admin/payment_made")
@admin_required
async def admin_payment_made():
    
    async with make_session() as sess:
        
        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        user = await sess.get(UserTable, int(current_user.auth_id))
        
        if user is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        payments_ = await sess.scalars(
            select(
                TotalPaymentsTable
            )
            .where(
                TotalPaymentsTable.user_id == user.id,
                TotalPaymentsTable.account == "craftlink",
                TotalPaymentsTable.is_received == False
            )
        )

        try:

            if payments_ is None:
                return jsonify({
                    "success": False,
                    "message": "No payments found"
                })

            payments = [
                {
                    "amount": payment.amount,
                    "date_time": payment.date_time.isoformat() if payment.date_time else None
                }
                for payment in payments_.all()
            ]
        except Exception as e:
            print(f"Error getting payments: {e}")

            return jsonify({
                "success": False,
                "message": "Error getting payments"
            })
        
        return jsonify({
            "success": True,
            "message": "Payments made",
            "payments": payments
        })
    

@admin_bp.get("/admin/payments/received")
@admin_required
async def admin_payments_received():
    
    async with make_session() as sess:
        
        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        user = await sess.get(UserTable, int(current_user.auth_id))
        
        if user is None:
            return jsonify({
                "success": False,
                "message": "You must be logged in to view payments"
            })
        
        payments_ = await sess.execute(
            select(
               TotalPaymentsTable
            )
            .where(
                TotalPaymentsTable.is_received == True,
                TotalPaymentsTable.account == "craftlink",
                TotalPaymentsTable.user_id == user.id
            )
        )

        if not payments_:
            return jsonify({
                "success": False,
                "message": "No payments found"
            })

        payments = [
            {
                "amount": payment.amount,
                "date_time": payment.date_time.isoformat() if payment.date_time else None
            }
            for payment in payments_.scalars().all()
        ]

        print(f"payments = {payments}")
        
        if not payments:
            return jsonify({
                "success": False,
                "message": "No payments found"
            })
        return jsonify({
            "success": True,
            "message": "Payments received",
            "payments": payments
        })