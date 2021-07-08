from starlette.requests import Request
from starlette.config import Config
import boto3

config = Config(".env")
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", cast=str)
AWS_SECRETY_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", cast=str)
AWS_REGION_NAME = config("AWS_REGION_NAME", cast=str)


s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRETY_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

def get_db(request: Request):
    return request.app.state._db

def get_s3_client():
    return s3_client