from enum import Enum


class StatusMarker(Enum):
    OK = 0
    WARNING = 1
    CRITICAL = 2


def get_int_marker_for_percentage(value: float, warn_at: float, critical_at: float) -> int:
    if value <= critical_at:
        return StatusMarker.CRITICAL.value
    elif value <= warn_at:
        return StatusMarker.WARNING.value
    else:
        return StatusMarker.OK.value


def get_resource_remaining_percent(used, total):
    if used is None:
        used = 0

    if 0 == total or total is None:
        return 0

    return 100 - ((used / total) * 100)


def get_resource_threshold_exceeded(threshold, used):
    if used is None:
        return 0

    return (used / threshold) * 100
