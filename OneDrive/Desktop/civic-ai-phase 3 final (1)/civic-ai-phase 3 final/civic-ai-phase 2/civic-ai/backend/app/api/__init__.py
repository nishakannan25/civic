from .auth import router as auth_router
from .users import router as users_router
from .incidents import router as incidents_router
from .notifications import router as notifications_router
from .community import router as community_router
from .sos import router as sos_router
from .departments import router as departments_router
from .ai import router as ai_router
from .admin import router as admin_router
from .citizen import router as citizen_router

__all__ = [
    "auth_router",
    "users_router",
    "incidents_router",
    "notifications_router",
    "community_router",
    "sos_router",
    "departments_router",
    "ai_router",
    "admin_router",
    "citizen_router",
]



