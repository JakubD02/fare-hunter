"""align route id types with models

Revision ID: f87427a998b2
Revises: 9d7de124400e
Create Date: 2026-10-12 15:48:43.834532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f87427a998b2'
down_revision: Union[str, Sequence[str], None] = '9d7de124400e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
