# app/routes/__init__.py
from app.routes.auth import router as auth_router
from app.routes.candidates import router as candidates_router
from app.routes.search import router as search_router
from app.routes.import_cv import router as import_router
from app.routes.gmail import router as gmail_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router

__all__ = ["auth_router", "candidates_router", "search_router", "import_router", "gmail_router", "analytics_router", "admin_router"]
