from fastapi import APIRouter

from app.api.applications import router as applications_router
from app.auth.google import router as google_auth_router

api_router = APIRouter()
api_router.include_router(applications_router)
api_router.include_router(google_auth_router)
