"""SmartMedical domain package."""

from .navigation import navigate_to_timetable_nr10  # re-export for convenience
from . import selectors  # keep selectors importable via package

__all__ = [
    "navigate_to_timetable_nr10",
    "selectors",
]
