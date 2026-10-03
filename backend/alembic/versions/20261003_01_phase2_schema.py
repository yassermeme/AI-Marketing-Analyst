"""Create the Phase 2 operational and analytical schema.

Revision ID: 20261003_01
Revises:
Create Date: 2026-10-03
"""

from alembic import op

from app.models import Base

revision = "20261003_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The canonical metadata is the single source of truth. Running it inside this
    # revision makes an empty PostgreSQL database reproducible through Alembic.
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=False)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=False)
