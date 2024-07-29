"""delete why destination column, add city of residence column

Revision ID: 7eb7841a3d71
Revises: a3d7e9272444
Create Date: 2024-07-21 15:51:24.574581

"""
from math import fabs
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7eb7841a3d71'
down_revision: Union[str, None] = 'a3d7e9272444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vacations', sa.Column('city_of_residence', sa.String(100)))
    op.drop_column('vacations', 'why_destination')


def downgrade() -> None:
    op.drop_column('vacations', 'city_of_residence')
    op.add_column('vacations', sa.Column('why_destination', sa.Text))
