import logging
from typing import Union, Optional, List

from gullveig import bootstrap_default_logger


# Configure default logging
def _configure_default_server_logger():
    logger = logging.getLogger('gullveig-server')
    bootstrap_default_logger(logger)


_configure_default_server_logger()


class AnalyticsSource:
    def __init__(self, remote: str, ident: str, mod: str) -> None:
        self.remote = remote
        self.ident: str = ident
        self.mod: str = mod


class AnalyticsStatusRecord:
    def __init__(self, source: AnalyticsSource, time: int, data: dict) -> None:
        self.source = source
        self.time = time

        self.subject: str = data['s']
        self.type: str = data['t']
        self.remaining: float = data['r']  # absolute percentage, None if not consumable
        self.state: int = data['st']  # status: 0 = ok, 1 = warn, 2 = crit, 3 = unknown
        self.is_metric: bool = data['m']  # Is related to metric

    @classmethod
    def clone(cls, source: AnalyticsSource, now: int, record: dict):
        return AnalyticsStatusRecord(source, now, {
            's': record['subject'],
            't': record['type'],
            'r': record['remaining'],
            'st': record['status'],
            'm': record['is_metric'],
        })


class HealthTransitionRecord:
    def __init__(self, source: AnalyticsSource, current: AnalyticsStatusRecord, before: int) -> None:
        self.source = source
        self.current = current
        self.before = before


class AnalyticsMetricRecord:
    def __init__(self, source: AnalyticsSource, time: int, data: dict) -> None:
        self.source = source
        self.time = time

        self.subject: str = data['s']
        self.metric: str = data['m']
        self.value: Union[int, float] = data['v']  # float or int
        self.range_from: Union[int, float] = data['f']  # float or int
        self.range_to: Union[int, float] = data['t']  # float or int
        self.display_as: str = data['d']


class AnalyticsMetaRecord:
    def __init__(self, source: AnalyticsSource, time: int, data: dict) -> None:
        self.source: AnalyticsSource = source
        self.time: int = time
        self.data: dict = data


class UpdateRequest:
    def __init__(self, source: AnalyticsSource, time: int):
        self.source = source
        self.time = time
        self.meta: Optional[AnalyticsMetaRecord] = None
        self.metrics: List[AnalyticsMetricRecord] = []
        self.status: List[AnalyticsStatusRecord] = []
        self.health: List[HealthTransitionRecord] = []
