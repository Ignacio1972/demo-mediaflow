"""
Seed initial categories to database
Run this script to populate the database with default categories
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.category import Category
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default categories for MediaFlow v2.1
# These are the most common categories used in radio/mall announcements
DEFAULT_CATEGORIES = [
    {
        "id": "pedidos",
        "name": "Pedidos Listos",
        "icon": "📦",
        "color": "#EF4444",  # Red
        "order": 0,
        "active": True,
    },
    {
        "id": "ofertas",
        "name": "Ofertas y Promociones",
        "icon": "🎉",
        "color": "#F97316",  # Orange
        "order": 1,
        "active": True,
    },
    {
        "id": "avisos",
        "name": "Avisos Generales",
        "icon": "📢",
        "color": "#3B82F6",  # Blue
        "order": 2,
        "active": True,
    },
    {
        "id": "musica",
        "name": "Mensajes Musicales",
        "icon": "🎵",
        "color": "#8B5CF6",  # Purple
        "order": 3,
        "active": True,
    },
    {
        "id": "eventos",
        "name": "Eventos",
        "icon": "🎪",
        "color": "#EC4899",  # Pink
        "order": 4,
        "active": True,
    },
    {
        "id": "horarios",
        "name": "Horarios y Servicios",
        "icon": "🕐",
        "color": "#14B8A6",  # Teal
        "order": 5,
        "active": True,
    },
    {
        "id": "seguridad",
        "name": "Seguridad",
        "icon": "🔔",
        "color": "#F59E0B",  # Amber
        "order": 6,
        "active": True,
    },
    {
        "id": "estacionamiento",
        "name": "Estacionamiento",
        "icon": "🚗",
        "color": "#6366F1",  # Indigo
        "order": 7,
        "active": True,
    },
    {
        "id": "shortcuts",
        "name": "Accesos Directos",
        "icon": "⚡",
        "color": "#10B981",  # Emerald
        "order": 99,
        "active": True,
    },
]


async def seed_categories():
    """Seed default categories into database"""
    async with AsyncSessionLocal() as session:
        try:
            logger.info("🌱 Starting category seeding...")

            added_count = 0
            skipped_count = 0

            for cat_data in DEFAULT_CATEGORIES:
                # Check if category already exists
                result = await session.execute(
                    select(Category).filter(Category.id == cat_data["id"])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(f"⏭️  Category '{cat_data['id']}' already exists, skipping")
                    skipped_count += 1
                    continue

                # Create new category
                category = Category(**cat_data)
                session.add(category)
                logger.info(
                    f"✅ Added category: {cat_data['icon']} {cat_data['name']} (id={cat_data['id']})"
                )
                added_count += 1

            # Commit all categories
            await session.commit()
            logger.info(f"\n🎉 Category seeding completed!")
            logger.info(f"   Added: {added_count}, Skipped: {skipped_count}")

            # Display summary
            result = await session.execute(
                select(Category).order_by(Category.order.asc())
            )
            all_categories = result.scalars().all()
            logger.info(f"\n📊 Total categories in database: {len(all_categories)}")
            print("\n" + "=" * 50)
            for cat in all_categories:
                status = "🟢" if cat.active else "🔴"
                print(f"{status} {cat.icon} {cat.name:<25} {cat.color} (id={cat.id})")
            print("=" * 50)

        except Exception as e:
            logger.error(f"❌ Error seeding categories: {str(e)}", exc_info=True)
            await session.rollback()
            raise


async def clear_categories():
    """Clear all categories from database (use with caution!)"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Category))
            categories = result.scalars().all()

            for cat in categories:
                await session.delete(cat)

            await session.commit()
            logger.info(f"🗑️  Deleted {len(categories)} categories from database")

        except Exception as e:
            logger.error(f"❌ Error clearing categories: {str(e)}", exc_info=True)
            await session.rollback()
            raise


async def list_categories():
    """List all categories in database"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Category).order_by(Category.order.asc())
        )
        categories = result.scalars().all()

        if not categories:
            logger.info("📭 No categories found in database")
            return

        logger.info(f"\n📊 Categories in database: {len(categories)}")
        print("\n" + "=" * 60)
        print(f"{'Status':<8} {'Icon':<4} {'Name':<25} {'Color':<10} {'ID':<15}")
        print("-" * 60)
        for cat in categories:
            status = "Active" if cat.active else "Inactive"
            print(f"{status:<8} {cat.icon:<4} {cat.name:<25} {cat.color:<10} {cat.id:<15}")
        print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--clear":
            logger.warning("⚠️  Clearing all categories from database...")
            asyncio.run(clear_categories())
        elif sys.argv[1] == "--list":
            asyncio.run(list_categories())
        else:
            print("Usage: python seed_categories.py [--clear|--list]")
            print("  --clear  Remove all categories")
            print("  --list   List all categories")
            print("  (no args) Seed default categories")
    else:
        asyncio.run(seed_categories())
