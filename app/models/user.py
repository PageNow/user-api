from re import L
from sqlalchemy import Table, Column, String, Boolean, Date, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import null, text, false

from app.db.db import metadata

user_table = Table(
    "user_info",
    metadata,
    Column("user_id", String, primary_key=True, index=True),
    Column(
        "user_uuid", UUID, nullable=False, unique=True,
        index=True, server_default=text("uuid_generate_v4()")
    ),
    Column("email", String, unique=True, nullable=False),
    Column("email_public", Boolean, server_default=false(), nullable=False),

    Column("first_name", String, nullable=False),
    Column("middle_name", String, nullable=False),
    Column("last_name", String, nullable=False),

    Column("dob", Date, nullable=False),
    Column("dob_public", Boolean, server_default=false(), nullable=False),

    Column("created_at", DateTime, server_default=func.now(), nullable=False),

    # share mode is either 'default_all' or 'default_none'
    Column("share_mode", String, server_default="default_all", nullable=False),
    Column("domain_allow_array", ARRAY(String), server_default="{}", nullable=False),
    Column("domain_deny_array", ARRAY(String), server_default="{}", nullable=False),

    # additional Info
    Column("gender", String, nullable=False),
    Column("gender_public", Boolean, server_default=false(), nullable=False),
    Column("school", String, server_default='', nullable=False),
    Column("school_public", Boolean, server_default=false(), nullable=False),
    Column("work", String, server_default='', nullable=False),
    Column("work_public", Boolean, server_default=false(), nullable=False),
    Column("location", String, server_default='', nullable=False),
    Column("location_public", Boolean, server_default=false(), nullable=False),
    Column("description", String, server_default='', nullable=False)
)
