"""Add default_voice_id to message_templates

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2025-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = '5365d58161fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'message_templates',
        sa.Column('default_voice_id', sa.String(50), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('message_templates', 'default_voice_id')
