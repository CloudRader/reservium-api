"""Rename Tables Names

Revision ID: aa608d47ad1f
Revises: b9460f13374f
Create Date: 2026-04-25 11:46:33.920605

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aa608d47ad1f"
down_revision: Union[str, None] = "b9460f13374f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- RENAME TABLES ---
    op.rename_table("user", "users")
    op.rename_table("calendar", "calendars")
    op.rename_table("event", "events")
    op.rename_table("mini_service", "mini_services")
    op.rename_table("reservation_service", "reservation_services")
    op.rename_table("calendar_collision_association", "calendar_collision_associations")
    op.rename_table("calendar_mini_service_association", "calendar_mini_service_associations")


def downgrade() -> None:
    # --- RENAME TABLES BACK ---
    op.rename_table("calendar_mini_service_associations", "calendar_mini_service_association")
    op.rename_table("calendar_collision_associations", "calendar_collision_association")
    op.rename_table("reservation_services", "reservation_service")
    op.rename_table("mini_services", "mini_service")
    op.rename_table("events", "event")
    op.rename_table("calendars", "calendar")
    op.rename_table("users", "user")
