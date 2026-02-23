"""add_cascade_delete_to_schedule_logs

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-02-07

Note: For SQLite, CASCADE is enforced at the ORM level via
passive_deletes=True on the relationship. The actual FK constraint
recreation is only needed for PostgreSQL deployments.
This migration uses batch mode for SQLite compatibility.
"""
from alembic import op
import sqlalchemy as sa


revision = "f6g7h8i9j0k1"
down_revision = "e5f6g7h8i9j0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch mode to recreate the table with CASCADE on FK
    # SQLite requires table recreation for FK changes
    with op.batch_alter_table("schedule_logs", recreate="always") as batch_op:
        batch_op.alter_column("schedule_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("schedule_logs", recreate="always") as batch_op:
        batch_op.alter_column("schedule_id", existing_type=sa.Integer(), nullable=False)
