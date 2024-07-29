"""add travel dates column to vacations table

Revision ID: a2573be115a5
Revises: bf4deaf80d32
Create Date: 2024-07-23 16:54:01.389092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2573be115a5'
down_revision: Union[str, None] = 'bf4deaf80d32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vacations', sa.Column('travel_dates', sa.String(100)))


def downgrade() -> None:
    op.drop_column('vacations', 'travel_dates')
