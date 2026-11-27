from fastapi import APIRouter
from app.core.database import check_database

router = APIRouter(tags=["system"])


@router.get("/health/database")
def database_health():
    try:
        check_database()
        return {"database": "connected"}
    except Exception:
        return {"database": "unavailable"}
