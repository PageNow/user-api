import os

from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

PROJECT_NAME = "pagenow-user-api"
VERSION = "1.0.0"

POSTGRES_USER = config("POSTGRES_USER", cast=str)
if "RDS_USERNAME" in os.environ:
    POSTGRES_USER = os.environ['RDS_USERNAME']

POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
if "RDS_PASSWORD" in os.environ:
    POSTGRES_PASSWORD = os.environ['RDS_PASSWORD']

POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
if "RDS_HOST" in os.environ:
    POSTGRES_SERVER = os.environ['RDS_HOST']

POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
if "RDS_PORT" in os.environ:
    POSTGRES_PORT = os.environ['RDS_PORT']

POSTGRES_DB = config("POSTGRES_DB", cast=str)
if "RDS_DB_NAME" in os.environ:
    POSTGRES_DB = os.environ['RDS_DB_NAME']

DATABASE_URL = config(
    "DATABASE_URL",
    cast=DatabaseURL,
    default=(
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}"
        f":{POSTGRES_PORT}/{POSTGRES_DB}"
    )
)
