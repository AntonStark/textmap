import typing as t

from core.models import Paragraph, Section

EventValidator = t.Callable[[str, dict], bool]


def build_section(event_type: str, event_body: dict) -> bool:
    return True


def union_section(event_type: str, event_body: dict) -> bool:
    return True


def border_section(event_type: str, event_body: dict) -> bool:
    return True


def offset_section(event_type: str, event_body: dict) -> bool:
    return True


def join_section(event_type: str, event_body: dict) -> bool:
    return True
