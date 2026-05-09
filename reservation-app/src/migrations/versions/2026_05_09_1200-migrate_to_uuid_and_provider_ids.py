"""Migrate to UUID primary keys and external provider IDs.

Revision ID: 49e8aba1a120
Revises: c3ebf15d446c
Create Date: 2026-05-09 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "49e8aba1a120"
down_revision: Union[str, None] = "c3ebf15d446c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. DROP ALL FOREIGN KEY CONSTRAINTS (Preparation)
    # Using the exact names found in previous migration files (they were singular).
    op.drop_constraint(
        op.f("fk_calendar_reservation_service_id_reservation_service"),
        "calendars",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_mini_service_reservation_service_id_reservation_service"),
        "mini_services",
        type_="foreignkey",
    )
    op.drop_constraint(op.f("fk_event_calendar_id_calendar"), "events", type_="foreignkey")
    op.drop_constraint(
        op.f("fk_calendar_collision_association_calendar_id_calendar"),
        "calendar_collision_associations",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_calendar_collision_association_collides_with_id_calendar"),
        "calendar_collision_associations",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_calendar_mini_service_association_calendar_id_calendar"),
        "calendar_mini_service_associations",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_calendar_mini_service_association_mini_service_id_mini_service"),
        "calendar_mini_service_associations",
        type_="foreignkey",
    )

    # 2. MIGRATE reservation_services (Cast current hex IDs to UUID and update PK name)
    op.drop_constraint(op.f("pk_reservation_service"), "reservation_services", type_="primary")
    op.execute("ALTER TABLE reservation_services ALTER COLUMN id TYPE uuid USING id::uuid")
    op.create_primary_key(op.f("pk_reservation_services"), "reservation_services", ["id"])

    # 3. MIGRATE mini_services (Cast current hex IDs to UUID and update PK name)
    op.drop_constraint(op.f("pk_mini_service"), "mini_services", type_="primary")
    op.execute("ALTER TABLE mini_services ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute(
        "ALTER TABLE mini_services ALTER COLUMN reservation_service_id TYPE uuid USING reservation_service_id::uuid"
    )
    op.create_primary_key(op.f("pk_mini_services"), "mini_services", ["id"])

    # 4. MIGRATE association tables primary keys (Cast to UUID)
    op.drop_constraint(
        op.f("pk_calendar_collision_association"),
        "calendar_collision_associations",
        type_="primary",
    )
    op.execute(
        "ALTER TABLE calendar_collision_associations ALTER COLUMN id TYPE uuid USING id::uuid"
    )
    op.create_primary_key(
        op.f("pk_calendar_collision_associations"), "calendar_collision_associations", ["id"]
    )

    op.drop_constraint(
        op.f("pk_calendar_mini_service_association"),
        "calendar_mini_service_associations",
        type_="primary",
    )
    op.execute(
        "ALTER TABLE calendar_mini_service_associations ALTER COLUMN id TYPE uuid USING id::uuid"
    )
    op.create_primary_key(
        op.f("pk_calendar_mini_service_associations"), "calendar_mini_service_associations", ["id"]
    )

    # 5. MIGRATE calendars (Google ID -> provider_id, New UUID PK)
    # Add new columns
    op.add_column("calendars", sa.Column("provider_id", sa.String(), nullable=True))
    op.add_column(
        "calendars",
        sa.Column("provider_name", sa.String(), server_default="google", nullable=False),
    )
    op.add_column("calendars", sa.Column("new_id", sa.UUID(), nullable=True))
    op.add_column("calendars", sa.Column("new_reservation_service_id", sa.UUID(), nullable=True))

    # Map Data
    op.execute(
        "UPDATE calendars SET provider_id = id, provider_name = 'google', new_id = gen_random_uuid(), new_reservation_service_id = reservation_service_id::uuid"
    )

    # Switch PK
    op.drop_constraint("pk_calendar", "calendars", type_="primary")
    op.drop_column("calendars", "id")
    op.drop_column("calendars", "reservation_service_id")
    op.alter_column("calendars", "new_id", new_column_name="id")
    op.alter_column(
        "calendars", "new_reservation_service_id", new_column_name="reservation_service_id"
    )
    op.create_primary_key(op.f("pk_calendars"), "calendars", ["id"])
    op.alter_column("calendars", "provider_id", nullable=False)
    op.create_index(op.f("ix_calendars_provider_id"), "calendars", ["provider_id"], unique=False)

    # 6. MIGRATE events (Google ID -> provider_id, New UUID PK)
    # Add new columns
    op.add_column("events", sa.Column("provider_id", sa.String(), nullable=True))
    op.add_column(
        "events", sa.Column("provider_name", sa.String(), server_default="google", nullable=False)
    )
    op.add_column("events", sa.Column("new_id", sa.UUID(), nullable=True))
    op.add_column("events", sa.Column("new_calendar_id", sa.UUID(), nullable=True))

    # Map Data (Join with calendars to get the new UUIDs)
    op.execute(
        "UPDATE events SET provider_id = id, provider_name = 'google', new_id = gen_random_uuid()"
    )
    op.execute("""
        UPDATE events e
        SET new_calendar_id = c.id
        FROM calendars c
        WHERE e.calendar_id = c.provider_id
    """)

    # Switch PK
    op.drop_constraint("pk_event", "events", type_="primary")
    op.drop_column("events", "id")
    op.drop_column("events", "calendar_id")
    op.alter_column("events", "new_id", new_column_name="id")
    op.alter_column("events", "new_calendar_id", new_column_name="calendar_id")
    op.create_primary_key(op.f("pk_events"), "events", ["id"])
    op.alter_column("events", "provider_id", nullable=False)
    op.create_index(op.f("ix_events_provider_id"), "events", ["provider_id"], unique=False)

    # 7. MIGRATE calendar_collision_associations (FK columns)
    op.add_column(
        "calendar_collision_associations", sa.Column("new_calendar_id", sa.UUID(), nullable=True)
    )
    op.add_column(
        "calendar_collision_associations",
        sa.Column("new_collides_with_id", sa.UUID(), nullable=True),
    )

    op.execute(
        "UPDATE calendar_collision_associations a SET new_calendar_id = c.id FROM calendars c WHERE a.calendar_id = c.provider_id"
    )
    op.execute(
        "UPDATE calendar_collision_associations a SET new_collides_with_id = c.id FROM calendars c WHERE a.collides_with_id = c.provider_id"
    )

    op.drop_column("calendar_collision_associations", "calendar_id")
    op.drop_column("calendar_collision_associations", "collides_with_id")
    op.alter_column(
        "calendar_collision_associations", "new_calendar_id", new_column_name="calendar_id"
    )
    op.alter_column(
        "calendar_collision_associations",
        "new_collides_with_id",
        new_column_name="collides_with_id",
    )
    op.alter_column("calendar_collision_associations", "calendar_id", nullable=False)
    op.alter_column("calendar_collision_associations", "collides_with_id", nullable=False)

    # 8. MIGRATE calendar_mini_service_associations (FK columns)
    op.add_column(
        "calendar_mini_service_associations", sa.Column("new_calendar_id", sa.UUID(), nullable=True)
    )
    op.add_column(
        "calendar_mini_service_associations",
        sa.Column("new_mini_service_id", sa.UUID(), nullable=True),
    )

    op.execute(
        "UPDATE calendar_mini_service_associations a SET new_calendar_id = c.id FROM calendars c WHERE a.calendar_id = c.provider_id"
    )
    op.execute(
        "UPDATE calendar_mini_service_associations a SET new_mini_service_id = m.id FROM mini_services m WHERE a.mini_service_id = m.id::text"
    )

    op.drop_column("calendar_mini_service_associations", "calendar_id")
    op.drop_column("calendar_mini_service_associations", "mini_service_id")
    op.alter_column(
        "calendar_mini_service_associations", "new_calendar_id", new_column_name="calendar_id"
    )
    op.alter_column(
        "calendar_mini_service_associations",
        "new_mini_service_id",
        new_column_name="mini_service_id",
    )
    op.alter_column("calendar_mini_service_associations", "calendar_id", nullable=False)
    op.alter_column("calendar_mini_service_associations", "mini_service_id", nullable=False)

    # 9. RESTORE ALL FOREIGN KEY CONSTRAINTS (Using New Naming Convention)
    op.create_foreign_key(
        op.f("fk_calendars_reservation_service_id_reservation_services"),
        "calendars",
        "reservation_services",
        ["reservation_service_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_mini_services_reservation_service_id_reservation_services"),
        "mini_services",
        "reservation_services",
        ["reservation_service_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_events_calendar_id_calendars"), "events", "calendars", ["calendar_id"], ["id"]
    )
    op.create_foreign_key(
        op.f("fk_calendar_collision_associations_calendar_id_calendars"),
        "calendar_collision_associations",
        "calendars",
        ["calendar_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_calendar_collision_associations_collides_with_id_calendars"),
        "calendar_collision_associations",
        "calendars",
        ["collides_with_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_calendar_mini_service_associations_calendar_id_calendars"),
        "calendar_mini_service_associations",
        "calendars",
        ["calendar_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_calendar_mini_service_associations_mini_service_id_mini_services"),
        "calendar_mini_service_associations",
        "mini_services",
        ["mini_service_id"],
        ["id"],
    )


def downgrade() -> None:
    # Reverting this complex migration is non-trivial and would require
    # restoring Google IDs as Primary Keys. It is recommended to backup
    # the database before applying the upgrade.
    pass
