from sqlalchemy import Table, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text

from app.db.db import metadata

share_notification_table = Table(
    'share_notification_table',
    metadata,
    Column(
        "event_id", UUID, primary_key=True,
        index=True, server_default=text("uuid_generate_v4()")
    ),
    # user who creates the notification
    Column("user_id", String, ForeignKey("user_table.user_id"),
           index=True),
    Column("sent_at", DateTime, server_default=func.now(),
           nullable=False),
    Column("url", String, nullable=False),
    Column("title", String, nullable=False),
    Column("sent_to", String, ForeignKey("user_table.user_id"), nullable=True)
)
