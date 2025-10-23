"""Conftest for testing schema."""

import pytest
from core.schemas import Rules


@pytest.fixture(scope="module")
def valid_rules():
    """Return rules schemas."""
    return Rules(
        night_time=True,
        reservation_without_permission=False,
        max_reservation_hours=4,
        in_advance_hours=2,
        in_advance_minutes=30,
        in_prior_days=7,
    )
