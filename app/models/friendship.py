from sqlalchemy import Table, Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKeyConstraint

from app.db.db import metadata

friendship_table = Table(
    'friendship',
    metadata,
    # user_id1 is the user that makes the friend request
    Column("user_id1", String, primary_key=True, index=True),
    Column("user_id2", String, primary_key=True, index=True),

    Column(
        "requested_at", DateTime, server_default=func.now(),
        nullable=False
    ),
    Column("accepted_at", DateTime, nullable=True),

    ForeignKeyConstraint(
        ['user_id1', 'user_id2'], ['user_info.user_id', 'user_info.user_id']
    )
)
