from fastapi import APIRouter

from .applications import router as oauth2_applications_router
from .scopes import router as oauth2_scopes_router
from .token import router as oauth2_token_router

router = APIRouter()

router.include_router(oauth2_applications_router, prefix="/oauth2", tags=["oauth2"])
router.include_router(oauth2_token_router, prefix="/oauth2", tags=["oauth2"])
router.include_router(oauth2_scopes_router, prefix="/oauth2", tags=["oauth2"])
