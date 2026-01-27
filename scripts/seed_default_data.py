#!/usr/bin/env python3
"""
MediaFlow v2.1 - Script de Datos Iniciales (Seed)

Crea las campañas, voces y configuraciones por defecto.
Es idempotente: puede ejecutarse múltiples veces sin duplicar datos.

Uso:
    cd /var/www/mediaflow/backend
    source venv/bin/activate
    python ../scripts/seed_default_data.py

O con Docker:
    docker-compose exec backend python /app/../scripts/seed_default_data.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Importar configuración
from app.core.config import settings

# ============================================
# DATOS POR DEFECTO
# ============================================

DEFAULT_CATEGORIES = [
    {
        "id": "pedidos",
        "name": "Ofertas de Temporada",
        "icon": "ShoppingCart",
        "color": "#22C55E",
        "order": 1,
        "ai_instructions": """Ofertas de Temporada

Ofertas de Temporada es una campaña flexible orientada a comunicar descuentos y promociones especiales en cualquier momento del año.
- Tono: Directo, entusiasta y con urgencia suave
- Debe generar sensación de oportunidad
- Destacar el ahorro o beneficio para el cliente
- Puede adaptarse a cualquier producto o servicio"""
    },
    {
        "id": "ofertas",
        "name": "Día de la Madre",
        "icon": "Heart",
        "color": "#F43F5E",
        "order": 2,
        "ai_instructions": """Día de la Madre
El Día de la Madre está ligado a reconocimiento, cariño y tiempo para demostrar afecto.
- Tono: Cálido, emotivo y cercano
- Destacar regalos especiales, experiencias compartidas
- Invitar a celebrar y agradecer
- Evitar lenguaje comercial frío"""
    },
    {
        "id": "avisos",
        "name": "Día del Padre",
        "icon": "Glasses",
        "color": "#3B82F6",
        "order": 3,
        "ai_instructions": """Día del Padre
El Día del Padre se asocia a celebración, cercanía y agradecimiento.
- Tono: Cercano, alegre y respetuoso
- Destacar experiencias, regalos prácticos o significativos
- Invitar a compartir tiempo de calidad
- Lenguaje inclusivo y familiar"""
    },
    {
        "id": "musica",
        "name": "Navidad",
        "icon": "Gift",
        "color": "#EC4899",
        "order": 4,
        "ai_instructions": """Navidad
Navidad es una época asociada a encuentro, celebración y momentos compartidos en familia.
- Tono: Festivo, cálido y acogedor
- Destacar regalos, decoración, comidas especiales
- Crear ambiente mágico y familiar
- Invitar a vivir la magia navideña"""
    },
    {
        "id": "eventos",
        "name": "Día del Niño",
        "icon": "Baby",
        "color": "#EC4899",
        "order": 5,
        "ai_instructions": """Día del Niño
El Día del Niño está asociado a juegos, alegría y experiencias compartidas.
- Tono: Divertido, alegre y dinámico
- Destacar juguetes, actividades, sorpresas
- Crear emoción y anticipación
- Lenguaje simple y entusiasta"""
    },
    {
        "id": "horarios",
        "name": "Pascua",
        "icon": "Rabbit",
        "color": "#8367D0",
        "order": 6,
        "ai_instructions": """Pascua de los Huevos de Chocolate
La Pascua está asociada a niños, juegos, regalos chocolatados y búsqueda de huevitos.
- Tono: Juguetón, mágico y familiar
- Destacar chocolates, búsquedas de huevitos, conejos
- Crear ambiente de diversión y sorpresa
- Ideal para actividades con niños"""
    },
    {
        "id": "seguridad",
        "name": "Fiestas Patrias",
        "icon": "PartyPopper",
        "color": "#3B82F6",
        "order": 7,
        "ai_instructions": """Fiestas Patrias
Fiestas Patrias están asociadas a celebrar las tradiciones chilenas, fondas, asados y tiempo en familia.
- Tono: Patriótico, festivo y tradicional
- Destacar comidas típicas, música, decoración
- Invitar a celebrar nuestras tradiciones
- Usar chilenismos apropiados"""
    },
    {
        "id": "estacionamiento",
        "name": "Especial Verano",
        "icon": "Sun",
        "color": "#6366F1",
        "order": 8,
        "ai_instructions": """Verano
El verano está asociado a sol, calor, panoramas, vacaciones y tiempo libre.
- Tono: Fresco, relajado y energético
- Destacar productos de temporada, actividades al aire libre
- Invitar a disfrutar el buen tiempo
- Crear sensación de libertad y diversión"""
    },
    {
        "id": "ano_nuevo",
        "name": "Año Nuevo",
        "icon": "Sparkles",
        "color": "#EA580C",
        "order": 9,
        "ai_instructions": """Año Nuevo
Año Nuevo está asociado a cierre de ciclo, nuevos comienzos y planificación.
- Tono: Esperanzador, festivo y renovador
- Destacar celebraciones, propósitos, ofertas de fin de año
- Invitar a cerrar bien el año y comenzar con energía
- Crear ambiente de expectativa positiva"""
    },
    {
        "id": "halloween",
        "name": "Halloween",
        "icon": "Bug",
        "color": "#2563EB",
        "order": 10,
        "ai_instructions": """Halloween
Halloween está asociado a diversión, juego, disfraces y experiencias de miedo controlado.
- Tono: Misterioso, divertido y juguetón
- Destacar disfraces, decoración, dulces, eventos temáticos
- Crear ambiente de diversión espeluznante
- Ideal para familias y niños"""
    },
    {
        "id": "black_friday",
        "name": "Black Friday",
        "icon": "Store",
        "color": "#16A34A",
        "order": 11,
        "ai_instructions": """Black Friday se asocian a promociones y descuentos increíbles. Muchas veces en tiendas pueden tener porcentajes que van desde un 15% a un 50%.
- Tono: Urgente, emocionante y directo
- Destacar descuentos específicos, tiempo limitado
- Crear sensación de oportunidad única
- Llamados a la acción claros"""
    },
    {
        "id": "devuelta_a_clases",
        "name": "Vuelta a Clases",
        "icon": "AcademicCap",
        "color": "#3B82F6",
        "order": 12,
        "ai_instructions": """Vuelta a Clases
La vuelta a clases marca el regreso de los niños al colegio. Se asocia a útiles escolares, uniformes y preparación.
- Tono: Organizado, práctico y motivador
- Destacar útiles, mochilas, uniformes, ofertas escolares
- Ayudar a padres a prepararse
- Crear sensación de nuevo comienzo"""
    },
    {
        "id": "especial_invierno",
        "name": "Especial Invierno",
        "icon": "Snowflake",
        "color": "#3B82F6",
        "order": 13,
        "ai_instructions": """Vacaciones de Invierno
Las vacaciones de invierno están asociadas a tiempo libre, actividades en familia y descanso.
- Tono: Acogedor, tranquilo y familiar
- Destacar actividades indoor, ropa de abrigo, panoramas
- Invitar a disfrutar el tiempo en familia
- Crear sensación de calidez y confort"""
    },
    {
        "id": "shortcuts",
        "name": "Accesos Directos",
        "icon": "Bolt",
        "color": "#10B981",
        "order": 99,
        "ai_instructions": ""
    }
]

DEFAULT_VOICES = [
    {
        "id": "juan_carlos",
        "name": "Juan Carlos",
        "elevenlabs_id": "G4IAP30yc6c1gK0csDfu",
        "is_default": True,
        "order": 1,
        "style": 0.0,
        "stability": 50.0,
        "similarity_boost": 75.0,
        "speed": 1.0,
        "use_speaker_boost": True,
        "volume_adjustment": 0.0
    },
    {
        "id": "yorman",
        "name": "Mario",
        "elevenlabs_id": "J2Jb9yZNvpXUNAL3a2bw",
        "is_default": False,
        "order": 2,
        "style": 0.0,
        "stability": 50.0,
        "similarity_boost": 75.0,
        "speed": 1.0,
        "use_speaker_boost": True,
        "volume_adjustment": 0.0
    },
    {
        "id": "veronica",
        "name": "Francisca",
        "elevenlabs_id": "Obg6KIFo8Md4PUo1m2mR",
        "is_default": False,
        "order": 3,
        "style": 0.0,
        "stability": 50.0,
        "similarity_boost": 75.0,
        "speed": 1.0,
        "use_speaker_boost": True,
        "volume_adjustment": 0.0
    },
    {
        "id": "sandra",
        "name": "Titi",
        "elevenlabs_id": "rEVYTKPqwSMhytFPayIb",
        "is_default": False,
        "order": 4,
        "style": 0.0,
        "stability": 50.0,
        "similarity_boost": 75.0,
        "speed": 1.0,
        "use_speaker_boost": True,
        "volume_adjustment": 0.0
    },
    {
        "id": "vale",
        "name": "Valeria",
        "elevenlabs_id": "cLzIVykddLltvgkzos6C",
        "is_default": False,
        "order": 5,
        "style": 0.0,
        "stability": 50.0,
        "similarity_boost": 75.0,
        "speed": 1.0,
        "use_speaker_boost": True,
        "volume_adjustment": 0.0
    }
]

DEFAULT_AI_CLIENTS = [
    {
        "id": "default",
        "name": "Cliente Genérico",
        "context": "Eres un experto en crear anuncios comerciales efectivos y atractivos para negocios locales. Genera anuncios cortos, claros y atractivos en español chileno. Evita usar emojis o caracteres especiales.",
        "category": "general",
        "is_default": True,
        "order": 0
    },
    {
        "id": "mall_generico",
        "name": "Centro Comercial",
        "context": "Eres un experto creando anuncios para centros comerciales y malls. Target: Familias, jóvenes y compradores frecuentes. Propuesta de valor: Variedad de tiendas, entretenimiento y experiencias únicas. Tono: Moderno, dinámico, acogedor. Genera anuncios cortos y atractivos en español chileno.",
        "category": "mall",
        "is_default": False,
        "order": 1
    },
    {
        "id": "supermercado_generico",
        "name": "Supermercado",
        "context": "Eres un experto creando anuncios para supermercados y tiendas de retail. Target: Familias chilenas, especialmente dueñas de casa. Propuesta de valor: Precios bajos y ofertas imperdibles. Tono: Cercano, confiable, ahorrativo, familiar. Genera anuncios cortos y efectivos en español chileno.",
        "category": "supermercado",
        "is_default": False,
        "order": 2
    }
]


# ============================================
# FUNCIONES DE SEED
# ============================================

async def seed_categories(session: AsyncSession):
    """Crear categorías (campañas) por defecto"""
    print("\n📁 Creando categorías...")

    for cat in DEFAULT_CATEGORIES:
        # Verificar si existe
        result = await session.execute(
            text("SELECT id FROM categories WHERE id = :id"),
            {"id": cat["id"]}
        )
        exists = result.fetchone()

        if exists:
            print(f"   ⏭️  {cat['name']} (ya existe)")
            continue

        # Insertar
        await session.execute(
            text("""
                INSERT INTO categories (id, name, icon, color, "order", active, ai_instructions, created_at, updated_at)
                VALUES (:id, :name, :icon, :color, :order, true, :ai_instructions, NOW(), NOW())
            """),
            {
                "id": cat["id"],
                "name": cat["name"],
                "icon": cat["icon"],
                "color": cat["color"],
                "order": cat["order"],
                "ai_instructions": cat.get("ai_instructions", "")
            }
        )
        print(f"   ✅ {cat['name']}")

    await session.commit()
    print(f"   Total: {len(DEFAULT_CATEGORIES)} categorías")


async def seed_voices(session: AsyncSession):
    """Crear voces por defecto"""
    print("\n🎙️ Creando voces...")

    for voice in DEFAULT_VOICES:
        # Verificar si existe
        result = await session.execute(
            text("SELECT id FROM voice_settings WHERE id = :id"),
            {"id": voice["id"]}
        )
        exists = result.fetchone()

        if exists:
            print(f"   ⏭️  {voice['name']} (ya existe)")
            continue

        # Insertar
        await session.execute(
            text("""
                INSERT INTO voice_settings (
                    id, name, elevenlabs_id, active, is_default, "order",
                    style, stability, similarity_boost, speed,
                    use_speaker_boost, volume_adjustment,
                    created_at, updated_at
                )
                VALUES (
                    :id, :name, :elevenlabs_id, true, :is_default, :order,
                    :style, :stability, :similarity_boost, :speed,
                    :use_speaker_boost, :volume_adjustment,
                    NOW(), NOW()
                )
            """),
            voice
        )
        default_mark = " [DEFAULT]" if voice["is_default"] else ""
        print(f"   ✅ {voice['name']}{default_mark}")

    await session.commit()
    print(f"   Total: {len(DEFAULT_VOICES)} voces")


async def seed_ai_clients(session: AsyncSession):
    """Crear clientes AI por defecto"""
    print("\n🤖 Creando clientes AI...")

    for client in DEFAULT_AI_CLIENTS:
        # Verificar si existe
        result = await session.execute(
            text("SELECT id FROM ai_clients WHERE id = :id"),
            {"id": client["id"]}
        )
        exists = result.fetchone()

        if exists:
            print(f"   ⏭️  {client['name']} (ya existe)")
            continue

        # Insertar
        await session.execute(
            text("""
                INSERT INTO ai_clients (
                    id, name, context, category, active, is_default, "order",
                    created_at, updated_at
                )
                VALUES (
                    :id, :name, :context, :category, true, :is_default, :order,
                    NOW(), NOW()
                )
            """),
            client
        )
        default_mark = " [DEFAULT]" if client["is_default"] else ""
        print(f"   ✅ {client['name']}{default_mark}")

    await session.commit()
    print(f"   Total: {len(DEFAULT_AI_CLIENTS)} clientes AI")


async def main():
    """Ejecutar todas las seeds"""
    print("=" * 50)
    print("  MediaFlow v2.1 - Datos Iniciales")
    print("=" * 50)

    # Crear engine
    database_url = settings.DATABASE_URL
    print(f"\n🔌 Conectando a: {database_url[:50]}...")

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            await seed_categories(session)
            await seed_voices(session)
            await seed_ai_clients(session)

            print("\n" + "=" * 50)
            print("  ✅ Datos iniciales creados exitosamente")
            print("=" * 50)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
