"""
AI Client Manager Service - v2.1
Manages AI clients/contexts for Claude API
"""
import logging
import time
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.ai_client import AIClient
from app.schemas.ai_client import AIClientCreate, AIClientUpdate

logger = logging.getLogger(__name__)


class AIClientManager:
    """Service for managing AI clients/contexts"""

    async def list_clients(
        self,
        db: AsyncSession,
        active_only: bool = True
    ) -> List[AIClient]:
        """List all AI clients"""
        query = select(AIClient)
        if active_only:
            query = query.where(AIClient.active == True)
        query = query.order_by(AIClient.order.asc(), AIClient.name.asc())

        result = await db.execute(query)
        return result.scalars().all()

    async def get_client(
        self,
        db: AsyncSession,
        client_id: str
    ) -> Optional[AIClient]:
        """Get a specific AI client by ID"""
        result = await db.execute(
            select(AIClient).where(AIClient.id == client_id)
        )
        return result.scalar_one_or_none()

    async def get_active_client(self, db: AsyncSession) -> Optional[AIClient]:
        """Get the currently active (default) AI client"""
        # First try to get the default client
        result = await db.execute(
            select(AIClient).where(AIClient.is_default == True)
        )
        client = result.scalar_one_or_none()

        # Fallback: first active client
        if not client:
            result = await db.execute(
                select(AIClient)
                .where(AIClient.active == True)
                .order_by(AIClient.order.asc())
                .limit(1)
            )
            client = result.scalar_one_or_none()

        return client

    async def get_active_client_id(self, db: AsyncSession) -> Optional[str]:
        """Get only the ID of the active client"""
        client = await self.get_active_client(db)
        return client.id if client else None

    async def set_active_client(
        self,
        db: AsyncSession,
        client_id: str
    ) -> bool:
        """Set a client as the active (default) one"""
        # Verify client exists
        client = await self.get_client(db, client_id)
        if not client:
            return False

        # Unset all defaults
        await db.execute(
            update(AIClient).values(is_default=False)
        )

        # Set new default
        await db.execute(
            update(AIClient)
            .where(AIClient.id == client_id)
            .values(is_default=True)
        )

        await db.commit()
        logger.info(f"⭐ Active AI client changed to: {client_id}")
        return True

    async def create_client(
        self,
        db: AsyncSession,
        data: AIClientCreate
    ) -> AIClient:
        """Create a new AI client"""
        # Generate ID if not provided
        client_id = data.id or f"custom_{int(time.time())}"

        # Get next order value
        result = await db.execute(select(AIClient))
        all_clients = result.scalars().all()
        next_order = max([c.order for c in all_clients], default=-1) + 1

        client = AIClient(
            id=client_id,
            name=data.name,
            context=data.context,
            category=data.category,
            active=data.active,
            is_default=False,  # New clients are not default by default
            order=next_order,
            settings=data.settings,
            custom_prompts=data.custom_prompts
        )

        db.add(client)
        await db.commit()
        await db.refresh(client)

        logger.info(f"➕ AI client created: {client_id}")
        return client

    async def update_client(
        self,
        db: AsyncSession,
        client_id: str,
        data: AIClientUpdate
    ) -> Optional[AIClient]:
        """Update an existing AI client"""
        client = await self.get_client(db, client_id)
        if not client:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        await db.commit()
        await db.refresh(client)

        logger.info(f"📝 AI client updated: {client_id}")
        return client

    async def delete_client(
        self,
        db: AsyncSession,
        client_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Delete an AI client with validations"""
        client = await self.get_client(db, client_id)
        if not client:
            return False, "Cliente no encontrado"

        # Cannot delete the active/default client
        if client.is_default:
            return False, "No se puede eliminar el cliente activo. Establece otro cliente como activo primero."

        # Cannot delete if it's the only one
        result = await db.execute(
            select(AIClient).where(AIClient.active == True)
        )
        count = len(result.scalars().all())
        if count <= 1:
            return False, "Debe existir al menos un cliente activo"

        await db.delete(client)
        await db.commit()

        logger.info(f"🗑️ AI client deleted: {client_id}")
        return True, None

    async def reorder_clients(
        self,
        db: AsyncSession,
        client_ids: List[str]
    ) -> bool:
        """Reorder AI clients"""
        for index, client_id in enumerate(client_ids):
            await db.execute(
                update(AIClient)
                .where(AIClient.id == client_id)
                .values(order=index)
            )

        await db.commit()
        logger.info(f"🔄 AI clients reordered: {client_ids}")
        return True


# Singleton instance
ai_client_manager = AIClientManager()
