
from app_factory import web_app

from itsdangerous.url_safe import (
    URLSafeSerializer, URLSafeTimedSerializer
)

import os

from dotenv import load_dotenv
load_dotenv(override=True)

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
APPLICATION_SALT = os.getenv("APPLICATION_SALT", "").strip()

serializer=URLSafeSerializer(
    secret_key=SECRET_KEY,
    salt=APPLICATION_SALT
)

timed_serializer=URLSafeTimedSerializer(
    secret_key=SECRET_KEY,
    salt=APPLICATION_SALT
)



async def password_maker(password) -> str|None:

    try:
        password_hash_ = await web_app.bcrypt.async_generate_password_hash(password)
        password_hash = password_hash_.decode("utf-8")
        
        return password_hash
    except:
        return None


def encode_with_itsdangerous(value) -> str|None:

    try:
        encoded = serializer.dumps(value)
        re_encoded = serializer.dumps(encoded)
        
        return re_encoded
    except:
        return None

def decode_with_itsdangerous(value) -> str|None:

    try:
        decoded = serializer.loads(value)
        re_decoded = serializer.loads(decoded)
        
        return re_decoded
    except:
        return None

def encode_with_itsdangerous_timed(value) -> str|None:

    try:
        encoded = timed_serializer.dumps(value)
        re_encoded = timed_serializer.dumps(encoded)
        
        return re_encoded
    except:
        return None


def decode_with_itsdangerous_timed(value) -> str|None:

    try:
        decoded = timed_serializer.loads(
            s=value,
            max_age=900 #15 mins
        )

        re_decoded = timed_serializer.loads(
            s=decoded,
            max_age=300 #5 mins
        )
        
        return re_decoded
    except:
        return None