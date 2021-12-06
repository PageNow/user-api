from sqlalchemy import Table, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.db import metadata

share_notification_seen_table = Table(
    'share_notification_seen_table',
    metadata,
    Column(
        "event_id", UUID, ForeignKey("share_notification_table.event_id"),
        primary_key=True, index=True
    ),
    # user who receives the notification
    Column("user_id", String, ForeignKey("user_table.user_id"),
           primary_key=True, index=True),
    Column("seen_at", DateTime, nullable=True)
)
