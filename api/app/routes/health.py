from fastapi import APIRouter
from api.app.database import check_database

router = APIRouter()


@router.get("/health")
def health_check():
    try:
        check_database()
        return {
            "status": "ok",
            "database": "connected",
            "service": "retailflow-api",
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
        }
