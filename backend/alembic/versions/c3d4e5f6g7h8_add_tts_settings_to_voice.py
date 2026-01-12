"""Add tts_settings column to voice_settings table

Revision ID: c3d4e5f6g7h8
Revises: 7b84a3a6206c
Create Date: 2026-01-07

TTS Settings for plain TTS without music:
- intro_silence: seconds of silence before voice
- outro_silence: seconds of silence after voice
- Useful for radio crossfade compatibility

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = '7b84a3a6206c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tts_settings column to voice_settings table (JSON)
    # Example: {"intro_silence": 1.0, "outro_silence": 1.0}
    op.add_column('voice_settings',
        sa.Column('tts_settings', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('voice_settings', 'tts_settings')
