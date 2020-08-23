from typing import Iterable

from aiosqlite import Connection


class DBI:
    def __init__(self) -> None:
        # noinspection PyTypeChecker
        self.db: Connection = None

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @staticmethod
    def get_table_for_period(period: str) -> str:
        if 'sec' == period:
            return 'metric_by_second'
        if 'min' == period:
            return 'metric_by_minute'
        if 'hou' == period:
            return 'metric_by_hour'
        if 'day' == period:
            return 'metric_by_day'
        if 'wee' == period:
            return 'metric_by_week'
        if 'mon' == period:
            return 'metric_by_month'
        if 'yea' == period:
            return 'metric_by_year'
        return None

    async def list_idents(self) -> Iterable:
        cursor = await self.db.execute(
            'SELECT '
            '   `ident`,'
            '   `version`,'
            '   `last_seen_at`,'
            '   `last_seen_from`'
            ' FROM `idents`'
            ' ORDER BY `ident`'
        )
        data = await cursor.fetchall()
        await cursor.close()
        return data

    async def get_server_version(self) -> Iterable:
        cursor = await self.db.execute('SELECT `version` FROM `gullveig` LIMIT 1')
        data = await cursor.fetchone()
        await cursor.close()
        return data['version']

    async def list_status(self) -> Iterable:
        cursor = await self.db.execute(
            'SELECT '
            '   `status`.`ident`, '
            '   `idents`.`version`, '
            '   `mod`, '
            '   `subject`, '
            '   `type`, '
            '   `remaining`, '
            '   `status`, '
            '   `is_metric`, '
            '   `updated_at`,'
            '   `last_seen_at`,'
            '   `last_seen_from`'
            ' FROM `status`'
            '   LEFT JOIN idents on status.ident = idents.ident '
            ' ORDER BY `status` DESC, `status`.`ident`, `mod`, `subject`, `type`'
        )
        data = await cursor.fetchall()
        await cursor.close()
        return data

    async def list_health(self) -> Iterable:
        cursor = await self.db.execute(
            'SELECT '
            '   `health`.`ident`, '
            '   `mod`, '
            '   `subject`, '
            '   `type`, '
            '   `remaining`, '
            '   `status`, '
            '   `before`, '
            '   `alert_sent`, '
            '   `is_metric`, '
            '   `updated_at`,'
            '   `last_seen_at`,'
            '   `last_seen_from`'
            ' FROM `health`'
            '   LEFT JOIN idents on health.ident = idents.ident '
            ' ORDER BY `updated_at` DESC, `health`.`ident`, `mod`, `subject`, `type` '
            ' LIMIT 25000'  # Don't be greedy
        )
        data = await cursor.fetchall()
        await cursor.close()
        return data

    async def list_meta_for_ident(self, ident: str) -> Iterable:
        cursor = await self.db.execute(
            'SELECT'
            '   `ident`,'
            '   `mod`,'
            '   `meta`,'
            '   `updated_at`'
            ' FROM `meta`'
            ' WHERE `ident` = :ident',
            {
                'ident': ident
            }
        )
        data = await cursor.fetchall()
        await cursor.close()
        return data

    async def get_metrics_for_ident(self, ident: str, period: str) -> Iterable:
        table = DBI.get_table_for_period(period)
        cursor = await self.db.execute(
            'SELECT '
            '   `time`,'
            '   `ident`,'
            '   `mod`,'
            '   `subject`,'
            '   `metric`,'
            '   `sum`,'
            '   `min`,'
            '   `max`,'
            '   `avg`,'
            '   `from`,'
            '   `to`,'
            '   `fmt`'
            ' FROM `%s` '
            '   WHERE `ident` = :ident'
            ' ORDER BY `mod`, `subject`, `metric`, `time`' % table,
            {
                'ident': ident
            }
        )
        data = await cursor.fetchall()
        await cursor.close()
        return data
