"""add_employee_call_templates

Revision ID: 5365d58161fb
Revises: d4e5f6g7h8i9
Create Date: 2026-01-25 20:00:45.788045

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '5365d58161fb'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


# Employee call templates seed data
EMPLOYEE_CALL_TEMPLATES = [
    {
        "id": "employee_call_default",
        "name": "Llamado estándar",
        "description": "Llamado formal con repetición",
        "template_text": "Atención: Se solicita la presencia de {nombre} en {ubicacion}. {nombre}, por favor acérquese a {ubicacion}. Gracias.",
        "variables": ["nombre", "ubicacion"],
        "module": "employee_call",
        "order": 0,
        "active": True,
        "is_default": True,
        "use_announcement_sound": True,
    },
    {
        "id": "employee_call_cliente",
        "name": "Llamado a cliente",
        "description": "Mensaje amable para clientes",
        "template_text": "Estimado cliente {nombre}, por favor diríjase a {ubicacion} donde le están esperando. Gracias.",
        "variables": ["nombre", "ubicacion"],
        "module": "employee_call",
        "order": 1,
        "active": True,
        "is_default": False,
        "use_announcement_sound": True,
    },
    {
        "id": "employee_call_corto",
        "name": "Llamado corto",
        "description": "Mensaje breve y directo",
        "template_text": "{nombre} a {ubicacion}, por favor.",
        "variables": ["nombre", "ubicacion"],
        "module": "employee_call",
        "order": 2,
        "active": True,
        "is_default": False,
        "use_announcement_sound": False,
    },
]


def upgrade() -> None:
    # Insert employee call templates
    message_templates = sa.table(
        'message_templates',
        sa.column('id', sa.String),
        sa.column('name', sa.String),
        sa.column('description', sa.String),
        sa.column('template_text', sa.String),
        sa.column('variables', sa.JSON),
        sa.column('module', sa.String),
        sa.column('order', sa.Integer),
        sa.column('active', sa.Boolean),
        sa.column('is_default', sa.Boolean),
        sa.column('use_announcement_sound', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime),
    )

    now = datetime.utcnow()
    for template in EMPLOYEE_CALL_TEMPLATES:
        op.execute(
            message_templates.insert().values(
                id=template["id"],
                name=template["name"],
                description=template["description"],
                template_text=template["template_text"],
                variables=template["variables"],
                module=template["module"],
                order=template["order"],
                active=template["active"],
                is_default=template["is_default"],
                use_announcement_sound=template["use_announcement_sound"],
                created_at=now,
                updated_at=now,
            )
        )


def downgrade() -> None:
    # Remove employee call templates
    op.execute(
        "DELETE FROM message_templates WHERE module = 'employee_call'"
    )
