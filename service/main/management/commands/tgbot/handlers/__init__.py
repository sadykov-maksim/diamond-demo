"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .echo import echo_router
from .user import user_router
from .profile import profile_router
from .support import support_router
from .pagination import *
from .games import game_router, barrel_router

routers_list = [
    admin_router,
    user_router,
    profile_router,
    support_router,
    game_router,
    barrel_router,
    echo_router,  # echo_router must be last
]

__all__ = [
    "routers_list",
]
