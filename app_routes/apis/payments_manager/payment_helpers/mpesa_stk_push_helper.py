
from datetime import datetime, timezone

import os

import requests


from .mpesa_helper_fuctions import (
    get_access_password, get_access_token
)
from helper_tools.web_security import encode_with_itsdangerous

from dotenv import load_dotenv

load_dotenv(override=True)


MPESA_PARTY_B = os.getenv("MPESA_PARTY_B", "").strip()


async def stk_push_helper(
        amount:int, phone_n:str, user_id:int,
        connects:int, reason:str
) -> str|None:

    """
    payment reasons:\n
    1.purchase_connects

    parameters:\n
    connects: number of connects purchased
    """

    if not connects or not user_id:
        return "invalid_args"

    print(f"MPESA_PARTY_B = {MPESA_PARTY_B}")

    if phone_n.startswith("0") and len(phone_n)==10:
        phone_number = f"254{phone_n[1:]}"
    elif phone_n.startswith("254") and len(phone_n)==12:
        phone_number = f"{phone_n}"
    else:
        return "invalid_n"

    print(f"phone_number = {phone_number}")
    
    signed_user_id = encode_with_itsdangerous(str(user_id))
    signed_purchased_connects = encode_with_itsdangerous(str(connects))
    reason_ = encode_with_itsdangerous(reason)
    
    date_time = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    
    url = f"{os.getenv('SAFARICOM_BASE_URL', '').strip()}/mpesa/stkpush/v1/processrequest"
    
    access_token = await get_access_token()
    
    password = await get_access_password(date_time)
    
    headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        
    payload = {
        "BusinessShortCode": MPESA_PARTY_B,
        "Timestamp": date_time,
        "Password": password,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": MPESA_PARTY_B,
        "PhoneNumber": phone_number,
        "CallBackURL": f"{os.getenv('CALL_BACK_BASE_URL', '').strip()}/mpesa/callback/{signed_user_id}/{signed_purchased_connects}/{reason_}",
        "AccountReference": "CraftLink",
        "TransactionDesc": "CraftLink Payments"
    }
    
    try:
        response = requests.post(
            url=url,
            json=payload,
            headers=headers,
            timeout=80
        )
    except Exception as e:
        print(f"Exception = {e}")
            
    print(f"response={response.json()}")