from fastapi import APIRouter

from .accounts import router as accounts_api_router
from .groups import router as groups_api_router

router = APIRouter()

# register api routers
router.include_router(accounts_api_router, prefix="/api", tags=["accounts"])
router.include_router(groups_api_router, prefix="/api", tags=["groups"])
