

import os

import boto3

from botocore.config import Config

#for enhanced intelligence and autocomplete for boto3
from boto3_type_annotations.s3 import client

from dotenv import load_dotenv
load_dotenv(override=True)

BUCKET_NAME=os.getenv("BUCKET_NAME", "").strip()
REGION_NAME=os.getenv("REGION_NAME", "").strip()
SECRET_ID=os.getenv("SECRET_ID", "").strip()
ACCESS_ID=os.getenv("ACCESS_ID", "").strip()
ENDPOINT=os.getenv("ENDPOINT", "").strip()



async def delete_obj_from_s3(file_name:str) ->None:
    
    s3_session = boto3.Session(
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key=SECRET_ID,
        region_name = REGION_NAME
    )

    s3_client = s3_session.client(
        service_name="s3",
        use_ssl=True,
        endpoint_url=ENDPOINT,
        #api_version = "v4"
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
    )

    try:

        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=file_name
        )

        print("file deleted from s3")

    except Exception as e:

        print(f"Error = {e}")