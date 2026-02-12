from .people import router as people_router
from .users import router as users_router
from .receipts import router as receipts_router

__all__ = ["people_router", "users_router", "receipts_router"]
