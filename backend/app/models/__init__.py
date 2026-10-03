"""SQLAlchemy models. Import this package so Alembic receives complete metadata."""

from app.models.analytics import *  # noqa: F403
from app.models.base import Base
from app.models.intelligence import *  # noqa: F403
from app.models.operational import *  # noqa: F403

__all__ = ["Base"]
