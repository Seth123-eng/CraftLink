

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



async def upload_file_with_a_presigned_url(
        file_type:str, file_name:str
) -> str | None:
    
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
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': file_name,
                'ContentType': file_type
                #'ACL': 'public-read'
            },
            ExpiresIn=36000,
            HttpMethod='PUT'
        )
        
        print(f"generated presigned url = {presigned_url}")


        return presigned_url
    
    except Exception as e:
        print(f"Error = {e}")
        print(f"Failed to generated presigned url")

        return None