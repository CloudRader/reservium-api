"""Utils for test package."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.models.base_class import Base


def as_dict(model: Base) -> Mapping[str, Any]:
    """
    Get dictionary from model.

    :param model: Model of type Base.
    :return dict[str, Any]: Dictionary of model.
    """
    return model.__dict__
