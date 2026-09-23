

from quart import Blueprint, jsonify, request

from helper_tools.web_security import decode_with_itsdangerous

from app_db_models.payment_info_model import (
    PaymentsTable, TotalPaymentsTable
)
from app_db_models.user_model import UserTable

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time
from helper_tools.award_connects_helper import award_connects

from sqlalchemy import select

import os

from dotenv import load_dotenv
load_dotenv(override=True)


from app_routes.apis.payments_manager.payment_helpers.purchase_connects_helper import purchase_connects


callback_bp = Blueprint("callback_bp", __name__)


#mpesa callback url, not intended to be visited explicitly
@callback_bp.post("/mpesa/callback/<user_id_>/<purchased_connects_>/<reason_>")
async def subscription_results(user_id_, purchased_connects_, reason_):
    
    user_id = decode_with_itsdangerous(user_id_)
    purchased_connects = decode_with_itsdangerous(purchased_connects_)
    reason = decode_with_itsdangerous(reason_)

    if not purchased_connects or not user_id or not reason:
        return jsonify({
            "success" : False,
            "msg" : "Payment failed"
        })

    print(f"user_id={user_id}")
    print(f"purchased_connects={purchased_connects}")
    print(f"reason={reason}")
    
    try:
        callback_data = await request.get_json()
        print("converted the response to json")
    except Exception as e:
        print("Failed to convert the response to json")
        print(f'Exception = {e}')
        
        return jsonify({
            #url for the error page with the message "payment failed"
        })
    
    print(f"results={callback_data}")
    
    callback_body = callback_data["Body"]
    
    stk_call_back_data = callback_body["stkCallback"]
    
    if stk_call_back_data["ResultCode"] == 0:
        
        callback_metadata = stk_call_back_data["CallbackMetadata"]
        
        amount = ""
        phone_number = ""
        mpesa_receipt_number = ""
        transaction_date = ""
        
        for item in callback_metadata["Item"]:
            if item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "PhoneNumber":
                phone_number = item["Value"]
            elif item["Name"] == "MpesaReceiptNumber":
                mpesa_receipt_number = item["Value"]
            elif item["Name"] == "TransactionDate":
                transaction_date = item["Value"]


        callback_data_entry = {
            "amount": amount,
            "phone_number": phone_number,
            "mpesa_receipt_number": mpesa_receipt_number,
            "result_code": stk_call_back_data["ResultCode"],
            "transaction_date": transaction_date,
            "status": "completed"
        }

        print(f"callback_data_entry={callback_data_entry}")

        async with make_session() as sess:

            try:
                amount=int(callback_data_entry.get("amount", ""))

                sess.add(
                    PaymentsTable(
                        amount=amount,
                        phone_number=str(callback_data_entry.get("phone_number")),
                        mpesa_receipt_number=callback_data_entry.get("mpesa_receipt_number"),
                        user_id=int(user_id),
                        is_received=False,
                        business_short_code=os.getenv("MPESA_PARTY_B", "").strip(),
                        date_time=await get_current_time(),
                        result_code=int(callback_data_entry.get("result_code", "")),
                        transaction_date=str(callback_data_entry.get("transaction_date"))
                    )
                )

                total_payment = await sess.scalar(
                    select(TotalPaymentsTable)
                    .where(
                        TotalPaymentsTable.account == "craftlink"
                    )
                )

                admin = await sess.scalar(
                    select(UserTable)
                    .where(
                        UserTable.account_type == "admin"
                    )
                )

                if total_payment:
                    total_payment.amount += amount
                else:

                    sess.add(
                        TotalPaymentsTable(
                            amount=amount,
                            account="craftlink",
                            date_time=await get_current_time(),
                            user_id=admin.id if admin else None
                        )
                    )
                    
                await sess.commit()

                if reason == "purchase_connects":
                    await purchase_connects(purchased_connects, int(user_id))
                    await award_connects(float(purchased_connects))

                return jsonify({
                    "success" : True,
                    "msg" : "Payment was successfull"
                })
            except Exception as e:
                print(f"Exception = {e}")

                await sess.rollback()

                return jsonify({
                    "success" : False,
                    "msg" : "Payment successfull, however an error occurred recording the payment"
                })
    else:
        
        return jsonify({
            "success" : False,
            "msg" : "Payment failed"
        })