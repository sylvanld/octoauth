from fastapi import APIRouter

from octoauth.views.authorize import router as oauth2_authorize_router
from octoauth.views.login import router as login_views_router
from octoauth.views.register import router as register_views_router

app = APIRouter()

# register views routers
app.include_router(login_views_router, include_in_schema=False)
app.include_router(register_views_router, include_in_schema=False)
app.include_router(oauth2_authorize_router, tags=["oauth2"])
