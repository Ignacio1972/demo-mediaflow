"""
Auth version endpoint for session invalidation
"""
from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

# Version file path (easy to edit)
VERSION_FILE = Path(__file__).parent.parent.parent.parent.parent / "auth_version.txt"

@router.get("/version")
async def get_auth_version():
    """Returns current auth version. When changed, all clients reload."""
    try:
        version = VERSION_FILE.read_text().strip()
    except FileNotFoundError:
        version = "v1"
    return {"version": version}
