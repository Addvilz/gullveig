import argparse
import logging
import ssl
from distutils.sysconfig import get_python_lib
from functools import partial
from glob import glob
from os import path

from aiohttp import web
from aiohttp.web import Application

from gullveig.common.configuration import Configuration, ConfigurationError
from gullveig.web.api import create_api_application

LOGGER = logging.getLogger('gullveig-web')

FILE_BASEDIR = path.dirname(__file__)
static_files_at = path.realpath(path.join(FILE_BASEDIR, '../webui/dist/'))

static_files = glob(static_files_at + '/**', recursive=True)


async def handle_static_request(file_path, _) -> web.FileResponse:
    return web.FileResponse(file_path)


def build_routing_table() -> list:
    routes = []

    # Load static files from file system and add them as static routes.
    # Avoids runtime static file resolution that is rather overkill in this case.
    for file in static_files:
        if not path.isfile(file):
            continue

        file_relative_path = path.relpath(file, static_files_at)
        handler = partial(handle_static_request, file)
        # noinspection PyTypeChecker
        route = web.get(('/%s' % file_relative_path), handler)
        routes.append(route)

    # Install default catch-all route
    index_file = path.join(static_files_at, 'index.html')
    index_handler = partial(handle_static_request, index_file)
    # noinspection PyTypeChecker
    index_catchall = web.get('/{tail:.*}', index_handler)
    routes.append(index_catchall)

    return routes


def start(config):
    application = Application(logger=LOGGER)
    api = create_api_application(config)

    root_routes = build_routing_table()
    application.add_subapp('/api', api)
    application.add_routes(root_routes)

    ssl_cert_path = config['web']['ssl_certificate']
    ssl_key_path = config['web']['ssl_certificate_key']

    ssl_cert_path_resolved = config.resolve_config_path(ssl_cert_path)
    ssl_key_path_resolved = config.resolve_config_path(ssl_key_path)

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.options &= ~ssl.OP_NO_SSLv3
    ssl_context.options &= ~ssl.OP_NO_SSLv2
    ssl_context.options &= ~ssl.OP_NO_TLSv1

    # ssl_context.

    ssl_context.load_cert_chain(ssl_cert_path_resolved, ssl_key_path_resolved)

    LOGGER.info('Web server listening on https://%s:%s', config['web']['bind_to'], config['web']['bind_port'])

    # noinspection PyTypeChecker
    web.run_app(
        host=config['web']['bind_to'],
        port=config['web'].getint('bind_port'),
        app=application,
        ssl_context=ssl_context,
        access_log=LOGGER,
        print=None
    )


def main():
    LOGGER.info('Gullveig Web UI starting')

    parser = argparse.ArgumentParser(description='Gullveig WWW UI')
    parser.add_argument(
        '--config',
        help='Web configuration file, defaults to /etc/gullveig/web.conf',
        default='/etc/gullveig/web.conf'
    )

    args = parser.parse_args()

    config = Configuration(
        args.config,
        {
            'web': {
                'bind_to': '127.0.0.1',
                'bind_port': '8765',
            },
            'server': {
                'data_dir': '/var/lib/gullveig'
            },
            'users': {}
        },
        {
            'web': ['ssl_certificate', 'ssl_certificate_key', 'secret']
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

    if config['web']['secret'] == 'CHANGEME':
        LOGGER.fatal('Refusing to start. You might want to take a closer look at the configuration.')
        exit(-1)

    start(config)
