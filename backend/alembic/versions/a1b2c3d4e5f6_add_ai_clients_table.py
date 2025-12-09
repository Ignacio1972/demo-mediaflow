"""Add ai_clients table

Revision ID: a1b2c3d4e5f6
Revises: 26383ecd31ac
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '26383ecd31ac'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_clients table
    op.create_table('ai_clients',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('context', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('order', sa.Integer(), nullable=False, default=0),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('custom_prompts', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default clients
    op.execute("""
        INSERT INTO ai_clients (id, name, context, category, active, is_default, "order", created_at, updated_at)
        VALUES (
            'default',
            'Cliente Generico',
            'Eres un experto en crear anuncios comerciales efectivos y atractivos para negocios locales. Genera anuncios cortos, claros y atractivos en espanol chileno. Evita usar emojis o caracteres especiales.',
            'general',
            1,
            1,
            0,
            datetime('now'),
            datetime('now')
        )
    """)

    op.execute("""
        INSERT INTO ai_clients (id, name, context, category, active, is_default, "order", settings, custom_prompts, created_at, updated_at)
        VALUES (
            'supermercado_ejemplo',
            'Supermercado Ejemplo',
            'Eres un experto creando anuncios para supermercados y tiendas de retail. Target: Familias chilenas, especialmente duenas de casa. Propuesta de valor: Precios bajos y ofertas imperdibles. Tono: Cercano, confiable, ahorrativo, familiar. Genera anuncios cortos y efectivos en espanol chileno.',
            'supermercado',
            1,
            0,
            1,
            '{"default_tone": "entusiasta", "language": "es-CL"}',
            '{"ofertas": "Enfocate en el ahorro y los precios bajos. Menciona descuentos especificos.", "informacion": "Usa Estimados clientes para mensajes operacionales."}',
            datetime('now'),
            datetime('now')
        )
    """)

    op.execute("""
        INSERT INTO ai_clients (id, name, context, category, active, is_default, "order", settings, custom_prompts, created_at, updated_at)
        VALUES (
            'mall_ejemplo',
            'Centro Comercial Ejemplo',
            'Eres un experto creando anuncios para centros comerciales y malls. Target: Familias, jovenes y compradores frecuentes. Propuesta de valor: Variedad de tiendas, entretenimiento y experiencias unicas. Tono: Moderno, dinamico, acogedor. Genera anuncios cortos y atractivos en espanol chileno.',
            'mall',
            1,
            0,
            2,
            '{"default_tone": "amigable", "language": "es-CL"}',
            '{"eventos": "Destaca la experiencia unica y la diversion. Menciona fecha y hora.", "horarios": "Comunica claramente los horarios de atencion."}',
            datetime('now'),
            datetime('now')
        )
    """)


def downgrade() -> None:
    op.drop_table('ai_clients')
