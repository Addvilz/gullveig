import argparse
import asyncio
import concurrent
import logging
import signal
import socket
import ssl
from concurrent.futures._base import Executor, CancelledError
from datetime import datetime
from os import path, sched_getaffinity

from aiohttp import ClientSession, ClientTimeout, ClientWebSocketResponse, ClientConnectorError, \
    WSServerHandshakeError, WSMsgType
from apscheduler.events import EVENT_JOB_EXECUTED, JobExecutionEvent
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from gullveig import GULLVEIG_VERSION
from gullveig.agent.modules import mod_facter, mod_fs, mod_res, mod_systemd, mod_apt, mod_osquery, mod_lwall, mod_pkg
from gullveig.agent.shmod import invoke_external_module, create_external_mod
from gullveig.common.alerting import FailureObserver, AlertManager
from gullveig.common.configuration import Configuration, ConfigurationError

LOGGER = logging.getLogger('gullveig-agent')
CONTEXT = {}
REPORT_BUFFER = {}
EMBEDDED_MODULES = {
    'mod_facter': {
        'get_report': mod_facter.get_report,
        'supports': mod_facter.supports,
        'key': mod_facter.key,
    },
    'mod_fs': {
        'get_report': mod_fs.get_report,
        'supports': mod_fs.supports,
        'key': mod_fs.key,
    },
    'mod_res': {
        'get_report': mod_res.get_report,
        'supports': mod_res.supports,
        'key': mod_res.key,
    },
    'mod_systemd': {
        'get_report': mod_systemd.get_report,
        'supports': mod_systemd.supports,
        'key': mod_systemd.key,
    },
    'mod_apt': {
        'get_report': mod_apt.get_report,
        'supports': mod_apt.supports,
        'key': mod_apt.key,
    },
    'mod_osquery': {
        'get_report': mod_osquery.get_report,
        'supports': mod_osquery.supports,
        'key': mod_osquery.key,
    },
    'mod_lwall': {
        'get_report': mod_lwall.get_report,
        'supports': mod_lwall.supports,
        'key': mod_lwall.key,
    },
    'mod_pkg': {
        'get_report': mod_pkg.get_report,
        'supports': mod_pkg.supports,
        'key': mod_pkg.key,
    }
}


def current_ts():
    return round(datetime.now().timestamp() * 1000)


def get_runtime_modules(module_config):
    runtime_modules = []

    for module, val in module_config.items():
        # Built in modules
        if module in EMBEDDED_MODULES.keys():
            is_enabled = module_config.getboolean(module)
            if not is_enabled:
                continue
            runtime_modules.append({'id': module, 'module': EMBEDDED_MODULES[module]})
            continue

        # External modules
        if 'mod_' == module[0:4]:
            LOGGER.error(
                'External module names must NOT use internal module prefix "mod_", prefix used for %s',
                module
            )
            exit(-1)

        runtime_modules.append({
            'id': module,
            'module': create_external_mod(module, val)
        })

    return runtime_modules


def invoke_module(module, config):
    if 'external' in module['module'] and module['module']['external'] is True:
        try:
            return invoke_external_module(module['module'])
        except BaseException as e:
            LOGGER.error('Failed to run external module, skipping - %s', e, exc_info=e)
            return None

    try:
        LOGGER.debug('Invoking internal module %s', module['module']['key']())

        if not module['module']['supports']():
            return None

        return {
            'module': module['module']['key'](),
            'report': module['module']['get_report'](config)
        }
    except BaseException as e:
        LOGGER.error('Failed to run module, skipping - %s', e, exc_info=e)
        return None


async def aggregate_pending_reports():
    if 0 == len(REPORT_BUFFER):
        return None

    data = {
        'meta': {'time': current_ts()},
        'mod_reports': []
    }

    expire_interval_s = CONTEXT['config']['agent'].getint('default_expires_after')
    expired_if_before_default = current_ts() - (expire_interval_s * 1000)

    for (job_id, job_result) in REPORT_BUFFER.items():
        if job_result is None:
            continue

        job_expired_if_before = expired_if_before_default
        module_reporting_config = CONTEXT['config']['module_reporting']
        module_expires_after_key = '%s_expires_after' % job_id

        if module_expires_after_key in module_reporting_config:
            module_expires_after = module_reporting_config.getint(module_expires_after_key)
            job_expired_if_before = current_ts() - (module_expires_after * 1000)
            LOGGER.debug('Validating cache for job %s is no older than %d seconds', job_id, module_expires_after)
        else:
            LOGGER.debug('Validating cache for job %s is no older than %d seconds (default)', job_id, expire_interval_s)

        if job_result['ts'] < job_expired_if_before:
            LOGGER.debug('Module report expired, ignoring - %s', job_id)
            REPORT_BUFFER[job_id] = None
            continue

        if job_result['is_reported']:
            # Keep pinging status, but ignore metrics and meta
            if 'status' not in job_result['result']['report']:
                LOGGER.debug('Skipping module report for %s - no status items', job_id)
                continue

            if 0 == len(job_result['result']['report']['status']):
                LOGGER.debug('Skipping module report for %s - no status items', job_id)
                continue

            LOGGER.debug('Will ping status for %s (cached)', job_id)

            data['mod_reports'].append({
                'module': job_result['result']['module'],
                'report': {
                    'status': job_result['result']['report']['status']
                },
            })
            continue

        data['mod_reports'].append(job_result['result'])

        job_result['is_reported'] = True

    if 0 == len(data['mod_reports']):
        return None

    return data


class ProtocolError(RuntimeError):
    pass


async def handle_socket(ws: ClientWebSocketResponse):
    report_delay = CONTEXT['config']['agent'].getint('report_delay')

    while True:
        LOGGER.debug('Creating report')

        time = datetime.now()
        report = await aggregate_pending_reports()
        elapsed = datetime.now() - time

        LOGGER.debug('Report created in %s', elapsed)

        if report is None:
            LOGGER.debug('Report is empty, skipping delivery and sleeping')
            await asyncio.sleep(report_delay)
            continue

        await ws.ping()

        resp = await ws.receive(timeout=CONTEXT['config']['agent'].getint('ping_timeout'))

        if resp.type == WSMsgType.CLOSED:
            raise ConnectionResetError()

        if resp.type != WSMsgType.PONG:
            raise ProtocolError('Expected pong, got %s' % resp.type)

        if ws.closed:
            LOGGER.debug('Server connection closed during pre-flight')
            raise ConnectionResetError()

        await ws.send_json(data=report)

        LOGGER.debug('Dumped report to socket, sleeping')

        await asyncio.sleep(report_delay)


async def handle_session(session: ClientSession, on_connected):
    server_url = 'https://%s:%s/' % (CONTEXT['server_host'], CONTEXT['server_port'])

    options = {
        'url': server_url,
        'ssl_context': CONTEXT['ssl_context'],
        'headers': {
            'x-client-key': CONTEXT['client_key'],
            'x-ident': CONTEXT['config']['agent']['ident'],
            'x-agent-version': GULLVEIG_VERSION
        },
        'autoping': False
    }

    async with session.ws_connect(**options) as web_socket:
        LOGGER.info('Connected to server at %s:%s', CONTEXT['server_host'], CONTEXT['server_port'])
        on_connected()
        await handle_socket(web_socket)


async def ws_client():
    server_ko_grace = CONTEXT['config']['agent'].getint('server_ko_grace')
    client_session_timeout = ClientTimeout(total=10)
    alert_manager = AlertManager(CONTEXT['config'], LOGGER)
    ko = FailureObserver(LOGGER)

    while True:
        try:
            async with ClientSession(timeout=client_session_timeout) as session:
                await handle_session(session, ko.reset)
        except ClientConnectorError as e:
            ko.mark_failure(e)
            LOGGER.error('Failed to connect to server - network error, connect call failed')
            LOGGER.debug('%s' % str(e))  # Original error
            await asyncio.sleep(CONTEXT['config']['agent'].getint('reconnect_delay'))
        except ConnectionResetError as e:
            ko.mark_failure(e)
            LOGGER.warning('Server connection reset')
            await asyncio.sleep(CONTEXT['config']['agent'].getint('reconnect_delay'))
        except concurrent.futures._base.TimeoutError as e:
            await session.close()
            ko.mark_failure(e)
            LOGGER.error('Server connection reset due to timeout')
            await asyncio.sleep(CONTEXT['config']['agent'].getint('reconnect_delay'))
        except ProtocolError as e:
            ko.mark_failure(e)
            LOGGER.warning('Server protocol error - %s', e)
            await asyncio.sleep(CONTEXT['config']['agent'].getint('reconnect_delay'))
        except WSServerHandshakeError as e:
            ko.mark_failure(e)
            # Authentication errors - these are permanent and will terminate the agent
            if e.status == 401:
                LOGGER.error('Server handshake failed - unauthorized')
                break
            elif e.status == 403:
                LOGGER.error('Server handshake failed - invalid credentials')
                break

            # Hopefully this is temporary so we will just retry in a while
            LOGGER.exception('Server handshake failed', e)
            await asyncio.sleep(CONTEXT['config']['agent'].getint('reconnect_delay'))
        finally:
            if ko.not_handled_for_more_than(server_ko_grace):
                await alert_manager.on_agent_server_comm_failure(ko.cause)
                ko.mark_handled()


async def shutdown(_signal, loop):
    LOGGER.info('Received %s, shutting down...', _signal.name)

    if 'scheduler' in CONTEXT:
        try:
            CONTEXT['scheduler'].shutdown()
        except BaseException as e:
            LOGGER.warning('Scheduler shutdown failed - %s', e)

    if hasattr(asyncio, 'all_tasks'):
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]
    else:
        tasks = [t for t in asyncio.Task.all_tasks() if t is not
                 asyncio.Task.current_task()]

    for task in tasks:
        task.cancel()

    LOGGER.debug('Terminating pending tasks')
    await asyncio.gather(*tasks, return_exceptions=False)
    loop.stop()


def on_job_complete(event: JobExecutionEvent):
    if not event.retval:
        # TODO: log
        return

    if not isinstance(event.retval, dict):
        # TODO LOG
        return

    REPORT_BUFFER[event.job_id] = {
        'job': event.job_id,
        'ts': current_ts(),
        'result': event.retval,
        'is_reported': False
    }


def schedule_reporting(modules, scheduler: BackgroundScheduler):
    default_fetch_every = CONTEXT['config']['agent'].getint('default_fetch_every')

    def get_module_delay(module_id):
        module_reporting_config = CONTEXT['config']['module_reporting']
        delay_key = '%s_fetch_every' % module_id

        if delay_key in module_reporting_config:
            module_specific_every = module_reporting_config.getint(delay_key)
            LOGGER.debug('Module %s is scheduled to run every %d seconds', module_id, module_specific_every)
            return module_specific_every

        LOGGER.debug('Module %s is scheduled to run every %d seconds (default)', module_id, default_fetch_every)

        return default_fetch_every

    [scheduler.add_job(
        invoke_module,
        'interval',
        seconds=get_module_delay(module['id']),
        max_instances=1,
        id=module['id'],
        name=module['id'],
        next_run_time=datetime.now(),  # Schedule first run to be ASAP
        args=[
            module,
            CONTEXT['config']
        ]
    ) for module in modules]

    scheduler.add_listener(on_job_complete, EVENT_JOB_EXECUTED)


def start(config):
    data_dir_cfg = config['agent']['data_dir']
    data_dir = config.resolve_config_path(data_dir_cfg)

    server_cert_path = path.join(data_dir, 'server.pem')
    client_conf_path = path.join(data_dir, 'client.conf')

    if not path.isfile(server_cert_path):
        LOGGER.error('Server certificate file does not exist - %s. Did you pair?', server_cert_path)
        exit(-1)

    client_config = Configuration(client_conf_path, {}, {'client': ['server_host', 'server_port', 'client_key']})

    if not client_config.is_file_path_valid():
        LOGGER.fatal('Client configuration file is not readable. Did you pair?')
        exit(-1)

    try:
        client_config.initialize()
    except ConfigurationError as e:
        LOGGER.fatal('Failed to initialize client configuration - %s', e)
        exit(-1)

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(server_cert_path)

    ssl_context.options &= ~ssl.OP_NO_SSLv3
    ssl_context.options &= ~ssl.OP_NO_SSLv2
    ssl_context.options &= ~ssl.OP_NO_TLSv1
    ssl_context.check_hostname = False  # We don't care really
    ssl_context.verify_mode = ssl.VerifyMode.CERT_REQUIRED

    CONTEXT['config'] = config
    CONTEXT['ssl_context'] = ssl_context
    CONTEXT['client_key'] = client_config['client']['client_key']
    CONTEXT['server_host'] = client_config['client']['server_host']
    CONTEXT['server_port'] = client_config['client']['server_port']

    num_workers = config['agent'].getint('mod_workers')
    LOGGER.debug('Will assign %d workers to mod execution', num_workers)
    CONTEXT['scheduler'] = BackgroundScheduler(
        logger=LOGGER,
        executors={
            'default': ProcessPoolExecutor(max_workers=num_workers)
        }
    )
    schedule_reporting(get_runtime_modules(config['modules']), CONTEXT['scheduler'])
    CONTEXT['scheduler'].start()

    LOGGER.debug('Starting ws_client')

    loop = asyncio.get_event_loop()

    for it in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        loop.add_signal_handler(it, lambda _si=it: asyncio.ensure_future(shutdown(_si, loop)))

    try:
        loop.run_until_complete(ws_client())
    except CancelledError:
        LOGGER.info('Terminated')
        exit(0)

    loop.close()


def main():
    parser = argparse.ArgumentParser(description='Gullveig reporting agent')
    parser.add_argument(
        '--config',
        help='Agent configuration file, defaults to /etc/gullveig/agent.conf',
        default='/etc/gullveig/agent.conf'
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

    LOGGER.info('Gullveig reporting agent starting')

    # By default, use half of the CPU cores available, minimum of 1, honoring affinity
    max_workers_default = int(max(len(sched_getaffinity(0)) / 2, 1))

    config = Configuration(
        args.config,
        {
            'agent': {
                'data_dir': '/var/lib/gullveig',
                'mod_workers': str(max_workers_default),
                'report_delay': '5',
                'reconnect_delay': '5',
                'server_ko_grace': '120',
                'ping_timeout': '1',
                'default_fetch_every': '5',
                'default_expires_after': '30',
            },
            'module_reporting': {
                'mod_pkg_fetch_every': '600',
                'mod_pkg_expires_after': '660',
            },
            'modules': {
                'mod_facter': 'True',
                'mod_fs': 'True',
                'mod_res': 'True',
                'mod_systemd': 'True',
                'mod_apt': 'False',
                'mod_osquery': 'False',
                'mod_lwall': 'False',
                'mod_pkg': 'True',
            },
            'mod_systemd': {},
            'mod_fs': {
                'ignore_ro': 'True'
            },
            'mod_osquery': {
                'config': 'osquery.yml'
            },
            'mod_lwall': {
                'policy_any': 'restrict',
                'policy_loopback': 'restrict',
                'policy_bound': 'restrict',
            },
            'mod_lwall_map': {},
            'mod_pkg': {
                'upgrade_warn': 'False',
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

    if 'ident' not in config['agent']:
        fqdn_parts = socket.getfqdn().split('.')
        fqdn_parts.reverse()
        r_fqdn = '.'.join(fqdn_parts)
        config['agent']['ident'] = r_fqdn
        LOGGER.debug('Set default ident from local fqdn - %s', config['agent']['ident'])

    start(config)
