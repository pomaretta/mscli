import logging
import urllib
import boto3
import json

from ..domain.credentials.credentials import Credentials

def get_json_from_s3(credentials: Credentials, bucket: str, key: str) -> dict:
    
    key = urllib.parse.unquote(key)

    logging.info(f"Getting JSON from S3: {bucket}/{key}")

    session = boto3.Session(
        aws_access_key_id=credentials.get_aws_access_key_id(),
        aws_secret_access_key=credentials.get_aws_secret_access_key(),
        region_name=credentials.get_aws_region()
    )

    s3 = session.resource('s3')
    obj = s3.Object(bucket, key)

    return json.loads(obj.get()['Body'].read().decode('utf-8'))