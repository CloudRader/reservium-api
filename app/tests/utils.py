"""
Utils for test package.
"""
from typing import Any

from db import Base


def as_dict(model: Base) -> dict[str, Any]:
    """Get dictionary from model.

    :param model: Model of type Base.
    :return dict[str, Any]: Dictionary of model.
    """
    return model.__dict__
