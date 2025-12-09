"""Add speed column to voice_settings table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-09

ElevenLabs 2025 API Update:
- Added speed parameter (0.7-1.2 range, default 1.0)
- This allows control over speech pace without affecting quality

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add speed column to voice_settings table
    # ElevenLabs 2025 API: speed parameter (0.7 = slow, 1.0 = normal, 1.2 = fast)
    op.add_column('voice_settings',
        sa.Column('speed', sa.Float(), nullable=False, server_default='1.0')
    )


def downgrade() -> None:
    op.drop_column('voice_settings', 'speed')
