import argparse
import logging
import mimetypes
import ssl
from functools import partial
from glob import glob
from os import path

from aiohttp import web
from aiohttp.hdrs import CONTENT_ENCODING
from aiohttp.web import Application

from gullveig import GULLVEIG_VERSION
from gullveig.common.configuration import Configuration, ConfigurationError
from gullveig.web.api import create_api_application

LOGGER = logging.getLogger('gullveig-web')
MIME = mimetypes.MimeTypes()

FILE_BASEDIR = path.dirname(__file__)
STATIC_FILES_AT = path.realpath(path.join(FILE_BASEDIR, '../webui/dist/'))
STATIC_FILE_LIST = glob(STATIC_FILES_AT + '/**', recursive=True)


async def handle_static_request(static_file, _) -> web.Response:
    # TODO - might do some E-TAG caching and verification here...?

    return web.Response(
        body=static_file['content'],
        content_type=static_file['content-type'],
        headers=static_file['headers']
    )


def build_routing_table(static_files) -> list:
    routes = []

    for mount_at, static_file in static_files.items():
        handler = partial(handle_static_request, static_file)
        # noinspection PyTypeChecker
        route = web.get(('/%s' % mount_at), handler)
        routes.append(route)

    # Install default catch-all route
    index_file = static_files['index.html']
    index_handler = partial(handle_static_request, index_file)
    # noinspection PyTypeChecker
    index_catchall = web.get('/{tail:.*}', index_handler)
    routes.append(index_catchall)

    return routes


def start(config):
    application = Application(logger=LOGGER)
    api = create_api_application(config)

    static_files = load_static_files_to_memory()
    root_routes = build_routing_table(static_files)

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


# Only server content from memory while in running.
# UI will otherwise fail if an update is installed.
def load_static_files_to_memory():
    static_files = {}
    for static_file in STATIC_FILE_LIST:
        if path.isdir(static_file):
            continue

        with open(static_file, 'rb') as res:
            headers = {}
            ct, encoding = mimetypes.guess_type(static_file)
            if not ct:
                ct = 'application/octet-stream'

            if encoding:
                headers[CONTENT_ENCODING] = encoding

            content = res.read()
            mount_at = path.relpath(static_file, STATIC_FILES_AT)

            static_files[mount_at] = {
                'content-type': ct,
                'content': content,
                'headers': headers
            }
    return static_files


def main():
    parser = argparse.ArgumentParser(description='Gullveig WWW UI')
    parser.add_argument(
        '--config',
        help='Web configuration file, defaults to /etc/gullveig/web.conf',
        default='/etc/gullveig/web.conf'
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

    LOGGER.info('Gullveig Web UI starting')

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
