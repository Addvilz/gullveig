import asyncio
import hashlib
import json
import logging
from crypt import crypt
from datetime import datetime
from functools import partial
from hmac import compare_digest

import aiosqlite
import jwt
from aiohttp.web import Application, RouteTableDef, Request, json_response
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import Response
from jwt import DecodeError, InvalidTokenError

from gullveig import GULLVEIG_VERSION
from gullveig.common.configuration import Configuration
from gullveig.web.dbi import DBI

LOGGER = logging.getLogger('gullveig-api')
api = RouteTableDef()
dbi = DBI()
CONTEXT = {}


def create_metric_key(mod, subject, metric):
    return hashlib.md5((mod + subject + metric).encode('utf-8')).hexdigest()


async def bootstrap(config: Configuration, _: Application) -> None:
    sqlite_db_path = config['server']['data_dir']
    sqlite_dsn = 'file:%s/gullveig.sqlite3?mode=ro&cache=private' % sqlite_db_path
    dbi.db = await aiosqlite.connect(sqlite_dsn)
    dbi.db.row_factory = DBI.dict_factory


async def shutdown(_: Application) -> None:
    if dbi.db is not None:
        await asyncio.shield(dbi.db.commit())
        await asyncio.shield(dbi.db.close())


@api.post('/sign-in/')
async def auth(request: Request):
    credentials = await request.json()

    if 'username' not in credentials:
        return json_response(
            data={'error': 'Missing username'},
            status=400
        )

    if 'password' not in credentials:
        return json_response(
            data={'error': 'Missing password'},
            status=400
        )

    local_users = CONTEXT['config']['users']
    username = credentials['username']
    password = credentials['password']

    if username not in local_users:
        return json_response(
            data={'error': 'Invalid credentials'},
            status=403
        )

    local_password = local_users[username]

    is_pw_valid = compare_digest(crypt(password, local_password), local_password)

    if not is_pw_valid:
        return json_response(
            data={'error': 'Invalid credentials'},
            status=403
        )

    token = jwt.encode(
        payload={
            'u': username,
            'iss': 'gullveig',
            'aud': 'gullveig',
            'iat': datetime.utcnow(),
            'nbf': datetime.utcnow(),
        },
        key=CONTEXT['config']['web']['secret'],
        algorithm='HS256'
    )

    try:
        remote = request.transport.get_extra_info('peername')[0]
    except BaseException as e:
        LOGGER.warning('Error while retrieving remote - %s', e)
        remote = '??? Unknown'

    LOGGER.info('User authenticated - %s from %s', username, remote)

    return json_response({'token': token.decode('ascii')})


@api.get('/ident/')
async def list_idents(_):
    idents = await dbi.list_idents()
    return json_response(idents)


@api.get('/versions/')
async def list_versions(_):
    server_version = await dbi.get_server_version()
    return json_response({
        'server': server_version,
        'web': GULLVEIG_VERSION
    })


@api.get('/status/')
async def list_status(_):
    server_version = await dbi.get_server_version()

    status = await dbi.list_status()
    status_list = []

    for it in status:
        if it['is_metric']:
            it['c'] = create_metric_key(it['mod'], it['subject'], it['type'])

        record_c = next((item for item in status_list if item['ident'] == it['ident']), None)

        if record_c is None:
            status_list.append({
                'ident': it['ident'],
                'agent_version': it['version'],
                'server_version': server_version,
                'last_seen_at': it['last_seen_at'],
                'last_seen_from': it['last_seen_from'],
                'health': 0,
                'items': []
            })
            record_c = status_list[-1]

        del it['ident']
        del it['version']
        del it['last_seen_at']
        del it['last_seen_from']

        record_c['items'].append(it)

        if record_c['health'] < it['status']:
            record_c['health'] = it['status']

    return json_response(status_list)


@api.get('/health/')
async def list_health(_):
    health = await dbi.list_health()
    health_list = []

    for it in health:
        if it['is_metric']:
            it['c'] = create_metric_key(it['mod'], it['subject'], it['type'])

        health_list.append(it)

    return json_response(health_list)


@api.get('/meta/{ident}/')
async def list_meta_for_ident(request: Request):
    metas = await dbi.list_meta_for_ident(request.match_info['ident'])

    for meta in metas:
        meta['meta'] = json.loads(meta['meta'])

    return json_response(metas)


@api.get('/metrics/{ident}/{period}/')
async def list_meta_for_ident(request: Request):
    metrics = await dbi.get_metrics_for_ident(
        request.match_info['ident'],
        request.match_info['period'],
    )

    charts = []

    for record in metrics:
        record_key = create_metric_key(record['mod'], record['subject'], record['metric'])

        record_c = next((item for item in charts if item['c'] == record_key), None)

        if record_c is None:
            record_c = {
                'c': record_key,
                'mod': record['mod'],
                'subject': record['subject'],
                'metric': record['metric'],
                'format': record['fmt'],
                'series': {
                    'min': [],
                    'max': [],
                    'avg': [],
                    'from': [],
                    'to': [],
                }
            }
            charts.append(record_c)

        record_c['series']['min'].append([record['time'], record['min']])
        record_c['series']['max'].append([record['time'], record['max']])
        record_c['series']['avg'].append([record['time'], record['avg']])

        record_c['series']['from'].append(record['from'])
        record_c['series']['to'].append(record['to'])

    for chart in charts:
        chart['min'] = min(chart['series']['from'])
        chart['max'] = max(chart['series']['to'])

        del chart['series']['from']
        del chart['series']['to']

    return json_response(charts)


@middleware
async def auth_middleware(request: Request, handler):
    if request.path != '/api/sign-in/':
        auth_token = request.headers.getone('x-auth-token')
        try:
            decoded = jwt.decode(
                jwt=auth_token,
                key=CONTEXT['config']['web']['secret'],
                issuer='gullveig',
                audience='gullveig',
                algorithms=['HS256']
            )

            local_users = CONTEXT['config']['users']

            if decoded['u'] not in local_users:
                LOGGER.warning('Access attempt with revoked username - %s', decoded['u'])

                return json_response(
                    data={'error': 'Revoked credentials'},
                    status=403
                )

        except DecodeError:
            return Response(status=401)
        except InvalidTokenError:
            return Response(status=401)

    response = await handler(request)
    return response


def create_api_application(config) -> Application:
    CONTEXT['config'] = config

    api_application = Application(logger=LOGGER, middlewares=[
        auth_middleware
    ])
    # noinspection PyTypeChecker
    api_application.on_startup.append(partial(bootstrap, config))
    api_application.on_shutdown.append(shutdown)
    api_application.add_routes(api)

    return api_application
