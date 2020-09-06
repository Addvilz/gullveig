import logging
import sys
from os import environ

GULLVEIG_VERSION = '0.1.12'


def bootstrap_default_logger(logger: logging.Logger):
    is_debug = environ.get('GULLVEIG_DEBUG') is not None

    if is_debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger.setLevel(log_level)

    stdout_fmt = logging.Formatter('%(levelname)-8s %(asctime)s %(message)s')

    stdout = logging.StreamHandler()
    stdout.setLevel(log_level)
    stdout.setFormatter(stdout_fmt)

    if hasattr(stdout, 'setStream'):
        stdout.setStream(sys.stdout)

    logger.addHandler(stdout)

    if is_debug:
        logger.debug('Debug logging is enabled')


def _configure_default_logger():
    logger = logging.getLogger('gullveig')
    bootstrap_default_logger(logger)


_configure_default_logger()
