"""make last_notified_at timezone aware

Revision ID: f5a7c92d6d7d
Revises: de0e3e0e666e
Create Date: 2026-11-03 14:17:20.307894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a7c92d6d7d'
down_revision: Union[str, Sequence[str], None] = 'de0e3e0e666e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert last_notified_at to timestamptz, treating existing values as UTC."""
    op.alter_column(
        "price_alerts",
        "last_notified_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using="last_notified_at AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    """Revert last_notified_at to naive timestamp in UTC."""
    op.alter_column(
        "price_alerts",
        "last_notified_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="last_notified_at AT TIME ZONE 'UTC'",
    )