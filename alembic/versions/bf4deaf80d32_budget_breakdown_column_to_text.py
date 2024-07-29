"""budget breakdown column to text

Revision ID: bf4deaf80d32
Revises: 7eb7841a3d71
Create Date: 2024-07-21 16:14:49.451465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf4deaf80d32'
down_revision: Union[str, None] = '7eb7841a3d71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('vacations', 'budget_breakdown', type_=sa.Text)


def downgrade() -> None:
    op.alter_column('vacations', 'budget_breakdown', type_=sa.String(300))
