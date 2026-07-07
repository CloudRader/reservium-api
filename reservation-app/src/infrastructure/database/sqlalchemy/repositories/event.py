"""
Define CRUD operations for the Event model.

Includes an abstract base class (AbstractCRUDEvent) and a concrete
implementation (CRUDEvent) using SQLAlchemy.
"""

from datetime import datetime
from uuid import UUID

from api.schemas import EventCreate, EventUpdate
from application.ports.repositories import EventRepository
from domain.models import CalendarModel, EventModel, EventState, ReservationServiceModel
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class SQLAlchemyEventRepository(
    SQLAlchemyBaseRepository[EventModel, EventCreate, EventUpdate], EventRepository
):
    """
    Concrete class for CRUD operations specific to the Event model.

    It extends the abstract AbstractCRUDEvent class and implements the required methods
    for querying and manipulating Event instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(EventModel, db)
        self.state = EventState
        self.calendar_model = CalendarModel
        self.reservation_service_model = ReservationServiceModel

    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> EventModel | None:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.calendar).joinedload(self.calendar_model.reservation_service),
                joinedload(self.model.user),
            )
            .execution_options(include_deleted=include_removed)
            .filter(self.model.id == id_)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_current_event_for_user(self, user_id: UUID) -> EventModel | None:
        now = datetime.now()

        stmt = (
            select(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.reservation_start <= now,
                self.model.reservation_end >= now,
            )
            .order_by(self.model.reservation_start.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_events_by_aliases(
        self,
        aliases: list[str],
        event_state: EventState | None = None,
        past: bool | None = None,
    ) -> list[EventModel]:
        now = datetime.now()

        stmt = (
            select(self.model)
            .join(self.calendar_model, self.model.calendar_id == self.calendar_model.id)
            .join(
                self.reservation_service_model,
                self.calendar_model.reservation_service_id == self.reservation_service_model.id,
            )
            .filter(self.reservation_service_model.alias.in_(aliases))
            .options(
                joinedload(self.model.calendar).joinedload(self.calendar_model.reservation_service),
                joinedload(self.model.user),
            )
            .order_by(self.model.reservation_start.desc())
        )

        if event_state is not None:
            stmt = stmt.filter(self.model.event_state == event_state)

        if past:
            stmt = stmt.filter(self.model.reservation_end < now)
        elif past is False:
            stmt = stmt.filter(self.model.reservation_start > now)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_overlapping_events(
        self,
        calendar_ids: list[UUID],
        start_time: datetime,
        end_time: datetime,
    ) -> list[EventModel]:
        stmt = select(self.model).filter(
            self.model.calendar_id.in_(calendar_ids),
            self.model.reservation_start < end_time,
            self.model.reservation_end > start_time,
            self.model.event_state != EventState.CANCELED,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
