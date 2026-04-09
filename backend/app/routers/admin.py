"""Admin and utility endpoints."""

from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/seed")
def seed_database() -> dict[str, str]:
    """Seed the database with sample data.
    
    Creates a sample trip (Wellington Zoo Field Trip) if none exist.
    Safe to call multiple times (idempotent).
    
    **Warning**: This endpoint should be protected with authentication in production.
    
    Returns:
        dict with status and message
        
    Example:
        POST /api/v1/admin/seed
        Response: {"status": "seeded", "message": "Database seeded successfully"}
    """
    from app.data.seed import main as seed_main

    try:
        seed_main()
        return {"status": "seeded", "message": "Database seeded successfully"}
    except Exception as e:
        logger.error(f"Seed failed: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring.
    
    Returns:
        dict with status
        
    Example:
        GET /api/v1/admin/health
        Response: {"status": "ok"}
    """
    return {"status": "ok"}
