from datetime import datetime, timedelta


def ts_current_second_start(ts: int) -> int:
    return ts - (ts % 1000)


def ts_current_minute_start(ts: int) -> int:
    return ts - (ts % 60000)


def ts_current_hour_start(ts: int) -> int:
    return ts - (ts % 3600000)


def ts_last_monday_start(ts: int) -> int:
    dt = datetime.fromtimestamp(ts / 1000.0)
    dt = dt - timedelta(days=dt.weekday() % 7)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return round(dt.timestamp() * 1000)


def ts_current_day_start(ts: int) -> int:
    dt = datetime.fromtimestamp(ts / 1000.0)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return round(dt.timestamp() * 1000)


def ts_current_month_start(ts: int) -> int:
    dt = datetime.fromtimestamp(ts / 1000.0)
    dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return round(dt.timestamp() * 1000)


def ts_current_year_start(ts: int) -> int:
    dt = datetime.fromtimestamp(ts / 1000.0)
    dt = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return round(dt.timestamp() * 1000)
