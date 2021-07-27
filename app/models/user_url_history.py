from sqlalchemy import Table, Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKeyConstraint

from app.db.db import metadata

user_url_history_table = Table(
    'user_url_history',
    metadata,
    Column('user_id', String, primary_key=True, index=True),
    Column('url', String, primary_key=True),
    Column(
        'accessed_at', DateTime, primary_key=True,
        server_default=func.now()
    ),
    Column('page_title', String, nullable=False, server_default=''),

    ForeignKeyConstraint(['user_id'], ['user_info.user_id'])
)
