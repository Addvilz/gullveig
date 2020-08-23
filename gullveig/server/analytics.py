from logging import Logger
from typing import List

from gullveig.server import UpdateRequest, AnalyticsSource, AnalyticsMetaRecord, AnalyticsMetricRecord, \
    AnalyticsStatusRecord, HealthTransitionRecord
from gullveig.server.dbi import DBI


class AnalyticsManager:
    def __init__(self, logger: Logger, dbi: DBI) -> None:
        self.logger = logger
        self.dbi = dbi

    async def handle_agent_report(self, remote: str, version: str, ident: str, payload: dict):
        if 'meta' not in payload:
            raise RuntimeError('Payload has no metadata - invalid report')

        if 'mod_reports' not in payload:
            raise RuntimeError('Payload has no mod_reports - invalid report')

        meta = payload['meta']

        if 'time' not in meta:
            raise RuntimeError('Payload metadata has no time - invalid report')

        time = meta['time']

        await self.dbi.update_ident_seen(remote, version, ident, time)

        requests: List[UpdateRequest] = []

        for mod_report in payload['mod_reports']:
            if 'module' not in mod_report:
                self.logger.warning('Report received from %s has invalid module report (no module name)')
                continue

            module = mod_report['module']
            report = mod_report['report']

            source = AnalyticsSource(remote, ident, module)
            request = UpdateRequest(source, time)

            if 'meta' in report:
                if report['meta']:
                    request.meta = AnalyticsMetaRecord(source, time, report['meta'])

            if 'metric' in report:
                for metric in report['metric']:
                    if not metric:
                        continue

                    request.metrics.append(AnalyticsMetricRecord(source, time, metric))

            if 'status' in report:
                for status in report['status']:
                    if not status:
                        continue

                    record = AnalyticsStatusRecord(source, time, status)
                    request.status.append(record)
                    current_status = await self.dbi.get_current_status(source, record.subject, record.type)

                    if current_status is None:
                        current_status = 3

                    if current_status != record.state:
                        request.health.append(HealthTransitionRecord(source, record, current_status))
                        self.logger.info(
                            'Service health changed from %d to %d for %s',
                            current_status, record.state, source.mod
                        )

            requests.append(request)

        await self.dbi.process_requests(requests)
