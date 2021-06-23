from sqlalchemy import Table, Column, String, Boolean, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text, false

from app.db.db import metadata

user_table = Table(
    "user_info",
    metadata,
    Column("user_id", String, primary_key=True, index=True),
    Column(
        "user_uuid", UUID(as_uuid=True), nullable=False, unique=True,
        index=True, server_default=text("uuid_generate_v4()")
    ),
    Column("email", String, unique=True, nullable=False),

    Column("first_name", String, nullable=False),
    Column("middle_name", String, nullable=False),
    Column("last_name", String, nullable=False),

    Column("dob", Date, nullable=False),
    Column("dob_public", Boolean, server_default=false(), nullable=False),

    Column("created_at", DateTime, server_default=func.now(), nullable=False)
)
