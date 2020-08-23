from typing import List, Optional

from gullveig.common.configuration import Configuration
from gullveig.server import UpdateRequest, AnalyticsSource, AnalyticsStatusRecord, HealthTransitionRecord
from gullveig.server.dbal.sqlite import SQLite3DBAL


class DBI:
    def __init__(self, config: Configuration) -> None:
        self.db: Optional[SQLite3DBAL] = None

    async def process_requests(self, requests: List[UpdateRequest]):
        for request in requests:
            try:
                async with self.db.scope() as scope:
                    if request.meta is not None:
                        await scope.write_meta(request.meta)

                    if 0 != len(request.metrics):
                        for metric in request.metrics:
                            await scope.write_metric(metric)

                    if 0 != len(request.status):
                        for status in request.status:
                            await scope.write_status(status)

                    if 0 != len(request.health):
                        for health in request.health:
                            await scope.write_health(health)

            except BaseException as e:
                raise e  # TODO

    async def process_status_update(self, status: AnalyticsStatusRecord, health: HealthTransitionRecord):
        async with self.db.scope() as scope:
            await scope.write_status(status)
            await scope.write_health(health)

    async def update_ident_seen(self, remote: str, version: str, ident: str, time: int):
        async with self.db.scope() as scope:
            await scope.update_last_seen(remote, version, ident, time)

    async def cleanup(self):
        retention_sec = {
            'second': 3600,  # 1h
            'minute': 86400,  # 24h
            'hour': 604800,  # 1w
            'day': 7776000,  # 3mo
            'week': 15770000,  # 6mo
            'month': 63070000,  # 2y
            'year': 157700000,  # 5y
        }

        async with self.db.scope() as scope:
            for period, max_age in retention_sec.items():
                await scope.purge_before(period, max_age * 1000)
                await scope.purge_health(604800*1000)

    async def get_pending_alerts(self):
        async with self.db.scope() as scope:
            return await scope.get_pending_alerts()

    async def mark_alerts_sent(self, ids: list):
        async with self.db.scope() as scope:
            return await scope.mark_alerts_sent(ids)

    async def get_current_status(self, source: AnalyticsSource, subject: str, t: str) -> int:
        async with self.db.scope() as scope:
            return await scope.get_current_status(
                ident=source.ident,
                mod=source.mod,
                subject=subject,
                t=t
            )

    async def list_all_status_records(self):
        async with self.db.scope() as scope:
            return await scope.list_all_status_records()
