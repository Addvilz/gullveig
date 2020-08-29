import argparse
import asyncio
import json
import logging
import signal
import ssl
from asyncio import CancelledError, shield
from contextlib import suppress
from datetime import datetime
from json import JSONDecodeError

from aiohttp import web, WSMsgType, WSMessage
from aiohttp.hdrs import UPGRADE
from aiohttp.web import Application, Request, Response
from aiohttp.web_runner import AppRunner, TCPSite

from gullveig import GULLVEIG_VERSION
from gullveig.common.alerting import AlertManager
from gullveig.common.configuration import Configuration, ConfigurationError
from gullveig.server import AnalyticsSource, AnalyticsStatusRecord, HealthTransitionRecord
from gullveig.server.analytics import AnalyticsManager
from gullveig.server.dbal.sqlite import SQLite3DBAL
from gullveig.server.dbi import DBI

LOGGER = logging.getLogger('gullveig-server')
CONTEXT = {}


async def handle_payload(remote: str, version: str, ident: str, payload: dict):
    await CONTEXT['analytics'].handle_agent_report(remote, version, ident, payload)


async def ws_handler(request: Request):
    remote = request.transport.get_extra_info('peername')[0]
    headers = request.headers

    if UPGRADE not in headers:
        return Response(status=400)

    if 'websocket' != headers[UPGRADE].lower().strip():
        return Response(status=400)

    if 'x-client-key' not in headers:
        LOGGER.warning('Websocket client attempt, no client key given from %s', remote)
        return Response(status=401)

    if headers['x-client-key'] != CONTEXT['client_key']:
        LOGGER.warning('Websocket client authentication failed from %s', remote)
        return Response(status=403)

    if 'x-ident' not in headers:
        LOGGER.warning('Websocket client attempt, no ident given from %s', remote)
        return Response(status=400)

    remote_ident = headers['x-ident']

    remote_version = '~0.1.4'
    if 'x-agent-version' in headers:
        remote_version = headers['x-agent-version']

    socket_response = web.WebSocketResponse(autoping=False)

    try:
        await socket_response.prepare(request)
    except BaseException as e:
        LOGGER.warning('Agent connection failure from %s, ident %s, %s', remote, remote_ident, e)
        raise e

    LOGGER.info('Agent connected from %s, ident %s, version %s', remote, remote_ident, remote_version)

    async for message in socket_response:
        message: WSMessage
        if WSMsgType.PING == message.type:
            LOGGER.debug('Received ping from %s, ident %s', remote, remote_ident)
            await socket_response.pong()
        elif WSMsgType.TEXT == message.type:
            LOGGER.debug('Received report from %s, ident %s', remote, remote_ident)

            try:
                payload = json.loads(message.data)
                await handle_payload(remote, remote_version, remote_ident, payload)
            except JSONDecodeError as e:
                LOGGER.exception('Failed to decode payload from %s, ident %s', remote, remote_ident, e)
            except BaseException as e:
                LOGGER.exception('Failed to handle payload from %s, ident %s', remote, remote_ident, e)

        elif WSMsgType.ERROR == message.type:
            LOGGER.debug('Received error from %s, ident %s, %s', remote, remote_ident, socket_response.exception())

    LOGGER.info('Agent disconnected - %s, ident %s', remote, remote_ident)

    return socket_response


async def server_worker(app, config, ssl_context):
    await CONTEXT['dbi'].db.bootstrap()

    runner = AppRunner(app=app, access_log=LOGGER, handle_signals=False)
    await runner.setup()

    site = TCPSite(
        runner=runner,
        host=config['server']['bind_to'],
        port=config['server'].getint('bind_port'),
        shutdown_timeout=5.0,
        ssl_context=ssl_context
    )

    loop = asyncio.get_event_loop()
    loop.create_task(database_cleanup_worker())
    loop.create_task(alerting_worker())
    loop.create_task(service_monitoring_worker())

    try:
        await site.start()
        while True:
            await asyncio.sleep(3600)  # Just hang around forever
    finally:
        await runner.cleanup()
        await shutdown_gracefully()


async def database_cleanup_worker():
    while True:
        try:
            LOGGER.debug('Compacting database')
            await CONTEXT['dbi'].cleanup()
            LOGGER.debug('Database compaction complete')
            await asyncio.sleep(30)  # compact every 30 seconds
        except CancelledError as e:
            raise e
        except BaseException as e:
            LOGGER.error('Error in database cleanup worker - %s', e)
            break
    await shutdown_gracefully()


async def alerting_worker():
    while True:
        try:
            LOGGER.debug('Processing alerts')
            alerts = await CONTEXT['dbi'].get_pending_alerts()
            if 0 != len(alerts):
                await CONTEXT['alert_manager'].dispatch_server_alerts(alerts)
                ids = [alert['id'] for alert in alerts]
                await CONTEXT['dbi'].mark_alerts_sent(ids)

            LOGGER.debug('Alerts processed')
            await asyncio.sleep(30)  # Check for alerts every 30 seconds
        except CancelledError as e:
            raise e
        except BaseException as e:
            LOGGER.error('Error in alerting worker - %s', e)
            break
    await shutdown_gracefully()


async def service_monitoring_worker():
    LOGGER.debug('Service monitoring worker entering grace')
    # Boot grace period - if server was offline, wait for 10 minutes before checking status of services
    # to give agents chance to reconnect and update the status before declaring them UNKNOWN
    await asyncio.sleep(600)
    LOGGER.debug('Service monitoring worker grace period done')

    while True:
        try:
            LOGGER.debug('Monitoring for absent services start')

            records = await CONTEXT['dbi'].list_all_status_records()
            now = int(datetime.now().timestamp() * 1000)
            max_age = int(now - (CONTEXT['service_timeout'] * 1000))

            for record in records:
                if 3 == record['status']:
                    continue  # Record already marked with outage

                is_expired = record['updated_at'] < max_age

                if is_expired:
                    source = AnalyticsSource('?', record['ident'], record['mod'])
                    status = AnalyticsStatusRecord.clone(source, now, record)
                    status.state = 3
                    health = HealthTransitionRecord(source, status, record['status'])

                    await CONTEXT['dbi'].process_status_update(status, health)

            LOGGER.debug('Monitoring for absent services complete')
            await asyncio.sleep(10)  # Check for service timeouts every 10 seconds
        except CancelledError as e:
            raise e
        except BaseException as e:
            LOGGER.error('Error service monitoring worker - %s', e)
            break
    await shutdown_gracefully()


async def shutdown_gracefully(_signal=None):
    # TODO: what was I thinking...
    if asyncio.shutdown is not False:
        return
    asyncio.shutdown = True

    if _signal is not None:
        LOGGER.info('Received %s, shutting down...', _signal.name)

    try:
        await shield(CONTEXT['dbi'].db.shutdown())
    except BaseException as e:
        LOGGER.warning('Could not shutdown DB gracefully - %s', e)

    if hasattr(asyncio, 'all_tasks'):
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]
    else:
        tasks = [t for t in asyncio.Task.all_tasks() if t is not
                 asyncio.Task.current_task()]

    LOGGER.debug('Terminating pending tasks')

    for task in tasks:
        task.cancel()

        with suppress(CancelledError):
            await task


def start(config: Configuration):
    asyncio.shutdown = False
    try:
        SQLite3DBAL.ensure_engine_version()
    except RuntimeError as e:
        LOGGER.fatal('%s', e)
        exit(-1)

    CONTEXT['client_key'] = config['server']['client_key']
    CONTEXT['dbi'] = DBI(config)
    CONTEXT['analytics'] = AnalyticsManager(LOGGER, CONTEXT['dbi'])
    CONTEXT['alert_manager'] = AlertManager(config, LOGGER)
    CONTEXT['service_timeout'] = config['server'].getint('service_timeout')

    sqlite_db_path = config['server']['data_dir']
    sqlite_dsn = 'file:%s/gullveig.sqlite3?mode=rwc&cache=shared' % sqlite_db_path
    sqlite = SQLite3DBAL(sqlite_dsn)

    CONTEXT['dbi'].db = sqlite

    server = Application(logger=LOGGER)
    server.add_routes([web.get('/', ws_handler)])

    ssl_cert_path = config['server']['ssl_certificate']
    ssl_key_path = config['server']['ssl_certificate_key']

    ssl_cert_path_resolved = config.resolve_config_path(ssl_cert_path)
    ssl_key_path_resolved = config.resolve_config_path(ssl_key_path)

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.options &= ~ssl.OP_NO_SSLv3
    ssl_context.options &= ~ssl.OP_NO_SSLv2
    ssl_context.options &= ~ssl.OP_NO_TLSv1

    ssl_context.load_cert_chain(ssl_cert_path_resolved, ssl_key_path_resolved)

    loop = asyncio.get_event_loop()

    for it in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        loop.add_signal_handler(it, lambda _si=it: (shield(shutdown_gracefully(_si))))

    try:
        LOGGER.info('Server listening on %s:%s', config['server']['bind_to'], config['server']['bind_port'])
        loop.run_until_complete(server_worker(server, config, ssl_context))
    except CancelledError:
        LOGGER.info('Server shutdown')
        exit(0)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.stop()


def main():
    parser = argparse.ArgumentParser(description='Gullveig reporting server')
    parser.add_argument(
        '--config',
        help='Server configuration file, defaults to /etc/gullveig/server.conf',
        default='/etc/gullveig/server.conf'
    )

    parser.add_argument(
        '-v', '--version',
        help='Print version and exit',
        action='store_true'
    )

    args = parser.parse_args()

    if args.version:
        print(GULLVEIG_VERSION)
        exit(0)

    LOGGER.info('Gullveig reporting server starting')

    config = Configuration(
        args.config, {
            'server': {
                'data_dir': '/var/lib/gullveig',
                'service_timeout': '120',
                'bind_to': '127.0.0.1',
                'bind_port': '8765'
            },
            'mail': {
                'enabled': 'False',
                'smtp_from': '',
                'smtp_to': '',
                'smtp_host': '',
                'smtp_port': '',
                'smtp_user': '',
                'smtp_password': '',
                'smtp_mode': 'tls'
            }
        },
        {
            'server': ['ssl_certificate', 'ssl_certificate_key', 'client_key'],
        }
    )

    if not config.is_file_path_valid():
        LOGGER.fatal('Configuration file is not readable - %s', args.config)
        exit(-1)

    try:
        config.initialize()
    except ConfigurationError as e:
        LOGGER.fatal(e)
        exit(-1)

    start(config)
