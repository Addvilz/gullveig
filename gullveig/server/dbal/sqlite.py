import json
import logging
import sqlite3
import threading
from datetime import datetime
from typing import Optional, List

import aiosqlite
from aiosqlite import Connection, Cursor

from gullveig import GULLVEIG_VERSION
from gullveig.server import AnalyticsMetaRecord, AnalyticsMetricRecord, AnalyticsStatusRecord, HealthTransitionRecord
from gullveig.server.date import ts_current_second_start, ts_current_minute_start, ts_current_hour_start, \
    ts_current_day_start, ts_last_monday_start, ts_current_month_start, ts_current_year_start

LOGGER = logging.getLogger('gullveig-server')


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLite3Pool:
    def __init__(self, dsn: str):
        self.local = threading.local()
        self.local.conn = None
        self.dsn = dsn
        self.pool: List[Connection] = []

    async def create(self) -> Connection:
        try:
            conn = await aiosqlite.connect(self.dsn, timeout=1, uri=True)
        except sqlite3.OperationalError as e:
            LOGGER.exception(e)
            LOGGER.fatal('Failed to open database %s', self.dsn)
            exit(-1)

        conn.row_factory = dict_factory
        self.pool.append(conn)
        return conn

    async def get_or_create(self) -> Connection:
        if self.local.conn is None:
            self.local.conn = await self.create()

        return self.local.conn

    async def cursor(self) -> Cursor:
        conn = await self.get_or_create()
        cursor = await conn.cursor()
        return cursor

    async def shutdown(self):
        for conn in self.pool:
            await conn.commit()
            await conn.close()

        self.pool.clear()

        LOGGER.debug('DB shutdown complete')


class SQLite3Scope:
    def __init__(self, pool: SQLite3Pool):
        self.pool = pool

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        conn = await self.pool.get_or_create()
        await conn.commit()

    async def update_last_seen(self, remote: str, version: str, ident: str, time: int):
        cursor = await self.pool.cursor()
        await cursor.execute(
            'INSERT INTO `idents` '
            ' (`ident`, `version`, `last_seen_at`, `last_seen_from`)'
            'VALUES (:ident, :version, :last_seen_at, :last_seen_from) '
            'ON CONFLICT (`ident`) '
            'DO UPDATE SET '
            '   `version` = :version, '
            '   `last_seen_at` = :last_seen_at, '
            '   `last_seen_from` = :last_seen_from ',
            {
                'ident': ident,
                'version': version,
                'last_seen_at': time,
                'last_seen_from': remote
            }
        )
        await cursor.close()

    async def write_meta(self, meta: AnalyticsMetaRecord):
        cursor = await self.pool.cursor()
        await cursor.execute(
            'INSERT INTO `meta` VALUES(:ident, :mod, :meta, :updated_at) '
            'ON CONFLICT (`ident`, `mod`) '
            'DO UPDATE SET '
            '   `meta` = :meta, '
            '   `updated_at` = :updated_at',
            {
                'ident': meta.source.ident,
                'mod': meta.source.mod,
                'meta': json.dumps(meta.data),
                'updated_at': meta.time
            }
        )
        await cursor.close()

    async def _upsert_metric(self, table: str, time: int, metric: AnalyticsMetricRecord):
        cursor = await self.pool.cursor()
        await cursor.execute(
            'INSERT INTO `%s`'
            'VALUES(:time, :ident, :mod, :subject, :metric, :value, :value, :value, :value, :from, :to, :fmt, 1) '
            'ON CONFLICT (`time`, `ident`, `mod`, `subject`, `metric`) '
            'DO UPDATE SET '
            '   `sum` = `sum` + :value, '
            '   `min` = CASE WHEN `min` > :value then :value else `min` end, '
            '   `max` = CASE WHEN `max` < :value then :value else `max` end, '
            '   `samples` = `samples` + 1, '
            '   `avg` = (`sum` + :value) / (`samples` + 1), '
            '   `from` = :from, '
            '   `to` = :to, '
            '   `fmt` = :fmt '
            % table,
            {
                'time': time,
                'ident': metric.source.ident,
                'mod': metric.source.mod,
                'subject': metric.subject,
                'metric': metric.metric,
                'value': metric.value,
                'from': metric.range_from,
                'to': metric.range_to,
                'fmt': metric.display_as,
            }
        )
        await cursor.close()

    async def write_metric(self, metric: AnalyticsMetricRecord):
        await self._upsert_metric('metric_by_second', ts_current_second_start(metric.time), metric)
        await self._upsert_metric('metric_by_minute', ts_current_minute_start(metric.time), metric)
        await self._upsert_metric('metric_by_hour', ts_current_hour_start(metric.time), metric)
        await self._upsert_metric('metric_by_day', ts_current_day_start(metric.time), metric)
        await self._upsert_metric('metric_by_week', ts_last_monday_start(metric.time), metric)
        await self._upsert_metric('metric_by_month', ts_current_month_start(metric.time), metric)
        await self._upsert_metric('metric_by_year', ts_current_year_start(metric.time), metric)

    async def write_status(self, status: AnalyticsStatusRecord):
        cursor = await self.pool.cursor()
        await cursor.execute(
            'INSERT INTO `status`'
            'VALUES(:ident, :mod, :subject, :type, :remaining, :status, :is_metric, :updated_at) '
            'ON CONFLICT (`ident`, `mod`, `subject`, `type`) '
            'DO UPDATE SET '
            '   `remaining` = :remaining, '
            '   `status` = :status, '
            '   `is_metric` = :is_metric, '
            '   `updated_at` = :updated_at ',
            {
                'ident': status.source.ident,
                'mod': status.source.mod,
                'subject': status.subject,
                'type': status.type,
                'remaining': status.remaining,
                'status': status.state,
                'is_metric': status.is_metric,
                'updated_at': status.time,
            }
        )
        await cursor.close()

    async def write_health(self, health: HealthTransitionRecord):
        cursor = await self.pool.cursor()
        await cursor.execute(
            'INSERT INTO `health` '
            '(ident, mod, subject, type, remaining, status, before, alert_sent, is_metric, updated_at) '
            'VALUES(:ident, :mod, :subject, :type, :remaining, :status, :before, 0, :is_metric, :updated_at) ',
            {
                'ident': health.source.ident,
                'mod': health.source.mod,
                'subject': health.current.subject,
                'type': health.current.type,
                'remaining': health.current.remaining,
                'status': health.current.state,
                'before': health.before,
                'is_metric': health.current.is_metric,
                'updated_at': health.current.time,
            }
        )
        await cursor.close()

    async def purge_before(self, period, max_age):
        period_tables = {
            'second': 'metric_by_second',
            'minute': 'metric_by_minute',
            'hour': 'metric_by_hour',
            'day': 'metric_by_day',
            'week': 'metric_by_week',
            'month': 'metric_by_month',
            'year': 'metric_by_year',
        }
        table = period_tables[period]

        cursor = await self.pool.cursor()

        await cursor.execute(
            'DELETE FROM `%s` WHERE `time` < :time' % table,
            {
                'time': int((datetime.now().timestamp() * 1000) - max_age)
            }
        )

        await cursor.close()

    async def purge_health(self, max_age):
        cursor = await self.pool.cursor()

        await cursor.execute(
            'DELETE FROM `health` WHERE `updated_at` < :time',
            {
                'time': int((datetime.now().timestamp() * 1000) - max_age)
            }
        )

        await cursor.close()

    async def get_current_status(self, ident: str, mod: str, subject: str, t: str) -> Optional[int]:
        cursor = await self.pool.cursor()

        result = await cursor.execute(
            'SELECT `status` FROM `status`'
            ' WHERE'
            '   `status`.`ident` = :ident'
            '   AND `status`.`mod` = :mod'
            '   AND `status`.`subject` = :subject'
            '   AND `status`.`type` = :type',
            {
                'ident': ident,
                'mod': mod,
                'subject': subject,
                'type': t
            }
        )

        record = await result.fetchone()
        await cursor.close()

        if record is None:
            return None

        return record['status']

    async def get_pending_alerts(self):
        cursor = await self.pool.cursor()
        result = await cursor.execute('SELECT * FROM `health` WHERE `alert_sent` = 0')
        records = await result.fetchall()
        await cursor.close()
        return records

    async def mark_alerts_sent(self, alert_ids: list):
        cursor = await self.pool.cursor()
        await cursor.execute(
            'UPDATE `health` SET `alert_sent` = 1 WHERE `id` IN(%s)' % ','.join('?' * len(alert_ids)),
            alert_ids
        )
        await cursor.close()

    async def list_all_status_records(self):
        cursor = await self.pool.cursor()
        result = await cursor.execute('SELECT * FROM `status`')
        records = await result.fetchall()
        await cursor.close()
        return records

    async def store_server_version(self):
        cursor = await self.pool.cursor()
        await cursor.execute('UPDATE `gullveig` SET `version` = :version WHERE true', {
            'version': GULLVEIG_VERSION
        })
        await cursor.close()


class SQLite3DBAL:
    def __init__(self, dsn):
        self.pool = SQLite3Pool(dsn)
        self.schema = SQLite3Schema()

    async def bootstrap(self):
        conn = await self.pool.get_or_create()
        cursor = await conn.cursor()
        await self.schema.migrate(cursor)
        await self.store_server_version()
        await cursor.close()
        await conn.commit()

    async def shutdown(self):
        await self.pool.shutdown()

    def scope(self):
        return SQLite3Scope(self.pool)

    @classmethod
    def ensure_engine_version(cls):
        (v_maj, v_min, _) = sqlite3.sqlite_version_info

        if v_maj > 3 or (3 == v_maj and v_min >= 24):
            return

        raise RuntimeError(
            'Incompatible SQLite3 version, minimum required version is 3.24.0, got %s'
            % sqlite3.sqlite_version
        )

    async def store_server_version(self):
        async with self.scope() as scope:
            await scope.store_server_version()


class SQLite3Schema:
    def __init__(self):
        self.migrations = {
            1: self.migrate_v1,
            2: self.migrate_v2,
        }

    async def migrate(self, cursor: Cursor):
        has_version_table = await cursor.execute(
            'SELECT `name`'
            ' FROM `sqlite_master`'
            ' WHERE `type`=\'table\' '
            '   AND `name`=\'gullveig\''
            ' LIMIT 1'
        )
        has_tables = (await has_version_table.fetchone()) is not None

        latest_version = max(self.migrations.keys())
        if not has_tables:
            current_version = 0
        else:
            c_db_ver = await cursor.execute('SELECT `db_version` FROM `gullveig` LIMIT 1')
            current_version = (await c_db_ver.fetchone())['db_version']

        LOGGER.debug('SQLITE3 schema - current v%d, latest v%d', current_version, latest_version)

        if current_version >= max(self.migrations.keys()):
            LOGGER.debug('SQLITE3 schema is up to date')
            # Latest version, nothing to do
            return

        delta = range(current_version + 1, latest_version + 1)
        for version in delta:
            LOGGER.debug('SQLITE3 - migrating to v%d', version)
            # noinspection PyArgumentList
            await self.migrations[version](cursor)
            LOGGER.debug('SQLITE3 - migrated to v%d', version)

    async def migrate_v1(self, cursor: Cursor):
        await cursor.execute('CREATE TABLE `gullveig` (`db_version` INTEGER NOT NULL)')

        await cursor.execute('INSERT INTO `gullveig` VALUES(1)')

        await cursor.execute('CREATE TABLE `idents` ('
                             '`ident` VARCHAR (255) NOT NULL,'
                             '`last_seen_at` INTEGER NOT NULL,'
                             '`last_seen_from` VARCHAR (45) NOT NULL,'
                             'PRIMARY KEY (`ident`)'
                             ')')

        await cursor.execute('CREATE INDEX `idx_idents_ident` ON `idents` (`ident`)')

        await cursor.execute('CREATE TABLE `meta` ('
                             '`ident` VARCHAR (255) NOT NULL, '
                             '`mod` VARCHAR (255) NOT NULL, '
                             '`meta` DATA JSON NOT NULL, '
                             '`updated_at` INTEGER NOT NULL, '
                             'PRIMARY KEY (`ident`, `mod`)'
                             ')')

        await cursor.execute('CREATE INDEX `idx_meta_ident` ON `meta` (`ident`)')
        await cursor.execute('CREATE INDEX `idx_meta_mod` ON `meta` (`mod`)')

        await cursor.execute('CREATE TABLE `status` ('
                             '`ident` VARCHAR (255) NOT NULL, '
                             '`mod` VARCHAR (255) NOT NULL, '
                             '`subject` VARCHAR (255) NOT NULL, '
                             '`type` VARCHAR (255) NOT NULL, '
                             '`remaining` NUMERIC NULLABLE DEFAULT NULL, '
                             '`status` INTEGER NOT NULL, '
                             '`is_metric` INTEGER NOT NULL, '
                             '`updated_at` INTEGER NOT NULL, '
                             'PRIMARY KEY (`ident`, `mod`, `subject`, `type`)'
                             ')')

        await cursor.execute('CREATE INDEX `idx_status_ident` ON `status` (`ident`)')
        await cursor.execute('CREATE INDEX `idx_status_updated_at` ON `status` (`updated_at`)')
        await cursor.execute('CREATE INDEX `idx_status_ident_updated_at` ON `status` (`ident`, `updated_at`)')

        await cursor.execute('CREATE TABLE `health` ('
                             '`id` INTEGER PRIMARY KEY AUTOINCREMENT, '
                             '`ident` VARCHAR (255) NOT NULL, '
                             '`mod` VARCHAR (255) NOT NULL, '
                             '`subject` VARCHAR (255) NOT NULL, '
                             '`type` VARCHAR (255) NOT NULL, '
                             '`remaining` NUMERIC NULLABLE DEFAULT NULL, '
                             '`status` INTEGER NOT NULL, '
                             '`before` INTEGER NOT NULL, '
                             '`alert_sent` INTEGER NOT NULL, '
                             '`is_metric` INTEGER NOT NULL, '
                             '`updated_at` INTEGER NOT NULL'
                             ')')

        await cursor.execute('CREATE INDEX `idx_health_ident` ON `health` (`ident`)')
        await cursor.execute('CREATE INDEX `idx_health_updated_at` ON `health` (`updated_at`)')
        await cursor.execute('CREATE INDEX `idx_health_alert_sent` ON `health` (`alert_sent`)')
        await cursor.execute('CREATE INDEX `idx_health_ident_updated_at` ON `health` (`ident`, `updated_at`)')

        metric_tables = [
            'metric_by_second',
            'metric_by_minute',
            'metric_by_hour',
            'metric_by_day',
            'metric_by_week',
            'metric_by_month',
            'metric_by_year',
        ]

        for table in metric_tables:
            await cursor.execute('CREATE TABLE `%s` ('
                                 '`time` INTEGER NOT NULL, '
                                 '`ident` VARCHAR (255) NOT NULL, '
                                 '`mod` VARCHAR (255) NOT NULL, '
                                 '`subject` VARCHAR (255) NOT NULL, '
                                 '`metric` VARCHAR (255) NOT NULL, '
                                 '`sum` NUMERIC NOT NULL, '
                                 '`min` NUMERIC NOT NULL, '
                                 '`max` NUMERIC NOT NULL, '
                                 '`avg` NUMERIC NOT NULL, '
                                 '`from` NUMERIC NOT NULL, '
                                 '`to` NUMERIC NOT NULL, '
                                 '`fmt` VARCHAR(10) NULL DEFAULT NULL, '
                                 '`samples` INTEGER NOT NULL, '
                                 'PRIMARY KEY (`time`, `ident`, `mod`, `subject`, `metric`)'
                                 ')' % table)

            await cursor.execute('CREATE INDEX `idx_{0}_t` ON `{0}` (`time`)'.format(table))
            await cursor.execute('CREATE INDEX `idx_{0}_ti` ON `{0}` (`time`,`ident`)'.format(table))
            await cursor.execute('CREATE INDEX `idx_{0}_tim` ON `{0}` (`time`,`ident`,`mod`)'.format(table))
            await cursor.execute('CREATE INDEX `idx_{0}_tims` ON `{0}` (`time`,`ident`,`mod`, `subject`)'.format(table))
            await cursor.execute(
                'CREATE INDEX `idx_{0}_timsm` ON `{0}` (`time`,`ident`,`mod`, `subject`, `metric`)'.format(table))

    async def migrate_v2(self, cursor: Cursor):
        await cursor.execute('ALTER TABLE `idents` ADD `version` VARCHAR(50) default \'unknown\' NOT NULL')
        await cursor.execute('ALTER TABLE `gullveig` ADD `version` VARCHAR(50) default \'unknown\' NOT NULL')
        await cursor.execute('UPDATE `gullveig` SET `db_version` = 2 WHERE true')
