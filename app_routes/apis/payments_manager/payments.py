


from quart import (
    Blueprint, request, jsonify, render_template
)

from quart_auth import current_user

from app_db_models.payment_info_model import PaymentsTable

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import login_required


from app_routes.apis.payments_manager.payment_helpers.mpesa_stk_push_helper import (
    stk_push_helper
)


from sqlalchemy import select


payments_bp = Blueprint("payments_bp", __name__)


@payments_bp.get("/payments_page")
@login_required
async def payments_page():

    return await render_template(
        "payments/payments_page.html"
    )


@payments_bp.get("/payments/info")
@login_required
async def payments_info():
    
    async with make_session() as sess:

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        

        # Get all payments where current user is either sender or receiver
        payments_ = await sess.execute(
            select(PaymentsTable)
            .where(
                PaymentsTable.user_id == int(current_user.auth_id),
            )
            .order_by(PaymentsTable.date_time.desc())
        )
        
        #displayed in a receipt style on the frontend
        payments = [
            {
                "id": payment.id,
                "amount": payment.amount,
                "date_time": payment.date_time.isoformat() if payment.date_time else None,
                "recepient": f"paid to CraftLink on {payment.date_time.strftime('%d %B %Y')}"
            }
            for payment in payments_.scalars().all()
        ]

        if payments:

            return jsonify({
                "success": True,
                "payments": payments
            })
        else:
            return jsonify({
                "success": False,
                "payments": []
            })
        


@payments_bp.post("/payments/purchase/connects")
@login_required
async def payments_purchase_connects():
    
    async with make_session() as sess:        

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        
        else:

            form = await request.form

            try:

                #resp = await stk_push_helper(
                #    amount=form.get("amount", ""),
                #    phone_n=form.get("phone_number", ""),
                #    user_id=int(current_user.auth_id),
                #    connects = form.get("connects", ""),
                #    reason="purchase_connects"
                #)

                #if resp == "invalid_n":
                #    return jsonify({
                #        "success" : True,
                #        "msg" : "Invalid Phone number"
                #    })

                #if resp == "invalid_args":
                #    return jsonify({
                #        "success" : True,
                #        "msg" : "Error processing request"
                #    })
                

                return jsonify({
                    "success" : True,
                    "msg" : "M-PESA Payments Under development, check back later"
                })
            except Exception as e:
                
                print(f"Exception = {e}")

                await sess.rollback()
                
                return jsonify({
                    "success" : False,
                    "msg" : "Ensure you have a payment"
                })