from sqlalchemy import Table, Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.db import metadata

friendship_table = Table(
    'friendship',
    metadata,
    # user_id1 is the user that makes the friend request
    Column("user_id1", String, ForeignKey("user_info.user_id"),
           primary_key=True, index=True),
    Column("user_id2", String, ForeignKey("user_info.user_id"),
           primary_key=True, index=True),

    Column(
        "requested_at", DateTime, server_default=func.now(),
        nullable=False
    ),
    Column("accepted_at", DateTime, nullable=True)
)
