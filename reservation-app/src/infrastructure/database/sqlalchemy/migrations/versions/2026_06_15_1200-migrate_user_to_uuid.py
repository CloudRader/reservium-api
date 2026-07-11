"""Migrate user to UUID primary key and add provider_id.

Revision ID: 59e8aba1a121
Revises: 49e8aba1a120
Create Date: 2026-06-15 12:00:00.000000

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "59e8aba1a121"
down_revision: Union[str, None] = "49e8aba1a120"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop foreign key constraint from events to users
    # It might be named fk_event_user_id_user or fk_events_user_id_users
    op.execute("ALTER TABLE events DROP CONSTRAINT IF EXISTS fk_event_user_id_user")
    op.execute("ALTER TABLE events DROP CONSTRAINT IF EXISTS fk_events_user_id_users")

    # 2. Migrate users table
    op.add_column("users", sa.Column("provider_id", sa.String(), nullable=True))
    op.add_column(
        "users", sa.Column("new_id", sa.UUID(), nullable=True, server_default=sa.text("uuidv7()"))
    )

    # Map data: provider_id = CAST(id AS VARCHAR), new_id = gen_random_uuid()
    op.execute("UPDATE users SET provider_id = CAST(id AS VARCHAR), new_id = gen_random_uuid()")

    # Switch PK
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS pk_user")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS pk_users")

    op.drop_column("users", "id")
    op.alter_column("users", "new_id", new_column_name="id", nullable=False)
    op.create_primary_key(op.f("pk_users"), "users", ["id"])

    op.alter_column("users", "provider_id", nullable=False)
    op.create_index(op.f("ix_users_provider_id"), "users", ["provider_id"], unique=True)

    # 3. Migrate events table (user_id column)
    op.add_column("events", sa.Column("new_user_id", sa.UUID(), nullable=True))

    # Map data: join with users to get new UUIDs
    op.execute("""
        UPDATE events e
        SET new_user_id = u.id
        FROM users u
        WHERE CAST(e.user_id AS VARCHAR) = u.provider_id
    """)

    op.drop_column("events", "user_id")
    op.alter_column("events", "new_user_id", new_column_name="user_id", nullable=False)

    # 4. Restore foreign key constraint
    op.create_foreign_key(op.f("fk_events_user_id_users"), "events", "users", ["user_id"], ["id"])


def downgrade() -> None:
    # Reverting this complex migration is non-trivial and would require
    # restoring integer IDs as Primary Keys. It is recommended to backup
    # the database before applying the upgrade.
    pass
