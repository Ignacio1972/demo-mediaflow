"""Add use_announcement_sound to message_templates

Revision ID: d4e5f6g7h8i9
Revises: 0df5c058911f
Create Date: 2025-01-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = '0df5c058911f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'message_templates',
        sa.Column('use_announcement_sound', sa.Boolean(), nullable=False, server_default='0')
    )


def downgrade() -> None:
    op.drop_column('message_templates', 'use_announcement_sound')
