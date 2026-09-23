
import os

import base64

import requests
from requests.auth import HTTPBasicAuth

from dotenv import load_dotenv

load_dotenv(override=True)


async def get_access_token():
    
    base_url = os.getenv('SAFARICOM_BASE_URL', "").strip()
    consumer_key = os.getenv("CONSUMER_KEY", "").strip()
    consumer_secret = os.getenv("CONSUMER_SECRET", "").strip()
    
    url = f"{base_url}/oauth/v1/generate?grant_type=client_credentials"
    
    #creates a temporary access token for authentication to daraja api
    response = requests.get(
        url=url,
        auth=HTTPBasicAuth(
            consumer_key,
            consumer_secret
        ),
        timeout=80
    )
    
    return response.json().get("access_token")


async def get_access_password(date_time):
    
    shortcode = os.getenv("MPESA_PARTY_B", "").strip()
    passkey = os.getenv("STK_PASSKEY", "").strip()
    
    data_to_encode = (
        shortcode + passkey + date_time
    )
    
    encode_data = base64.b64encode(
        data_to_encode.encode()
    )
    
    return encode_data.decode("utf-8")