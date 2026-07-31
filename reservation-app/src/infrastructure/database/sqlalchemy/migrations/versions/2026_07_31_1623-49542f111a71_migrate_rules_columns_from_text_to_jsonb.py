"""Migrate Rules Columns from TEXT to JSONB

Revision ID: 49542f111a71
Revises: f079343cf7ed
Create Date: 2026-07-31 16:23:02.410443

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "49542f111a71"
down_revision: Union[str, None] = "f079343cf7ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "calendars",
        "club_member_rules",
        existing_type=sa.VARCHAR(),
        type_=postgresql.JSONB(),
        postgresql_using="club_member_rules::jsonb",
        nullable=False,
    )
    op.alter_column(
        "calendars",
        "active_member_rules",
        existing_type=sa.VARCHAR(),
        type_=postgresql.JSONB(),
        postgresql_using="active_member_rules::jsonb",
        existing_nullable=False,
    )
    op.alter_column(
        "calendars",
        "manager_rules",
        existing_type=sa.VARCHAR(),
        type_=postgresql.JSONB(),
        postgresql_using="manager_rules::jsonb",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "calendars",
        "manager_rules",
        existing_type=postgresql.JSONB(),
        type_=sa.VARCHAR(),
        postgresql_using="manager_rules::varchar",
        existing_nullable=False,
    )
    op.alter_column(
        "calendars",
        "active_member_rules",
        existing_type=postgresql.JSONB(),
        type_=sa.VARCHAR(),
        postgresql_using="active_member_rules::varchar",
        existing_nullable=False,
    )
    op.alter_column(
        "calendars",
        "club_member_rules",
        existing_type=postgresql.JSONB(),
        type_=sa.VARCHAR(),
        postgresql_using="club_member_rules::varchar",
        existing_nullable=True,
    )
