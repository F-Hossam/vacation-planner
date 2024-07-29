"""change the type of vacations columns fron string to text

Revision ID: a3d7e9272444
Revises: 
Create Date: 2024-07-18 23:41:50.544055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3d7e9272444'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('vacations', 'iternary', type_=sa.Text)
    op.alter_column('vacations', 'why_destination', type_=sa.Text)

def downgrade() -> None:
    op.alter_column('vacations', 'iternary', type_=sa.String(21845))
    op.alter_column('vacations', 'why_destination', type_=sa.String(1000))
