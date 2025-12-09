"""
AI Client Serializer
Converts AIClient model to API response format
"""
from typing import Dict, Any
from app.models.ai_client import AIClient


def serialize_ai_client(client: AIClient) -> Dict[str, Any]:
    """
    Serialize an AIClient model to a dictionary for API response.

    Args:
        client: AIClient model instance

    Returns:
        Dictionary with client data formatted for API response
    """
    return {
        "id": client.id,
        "name": client.name,
        "context": client.context,
        "category": client.category,
        "active": client.active,
        "is_default": client.is_default,
        "order": client.order,
        "settings": client.settings,
        "custom_prompts": client.custom_prompts,
        "created_at": client.created_at.isoformat() if client.created_at else None,
        "updated_at": client.updated_at.isoformat() if client.updated_at else None,
    }
