import logging
import sys
from os import environ


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
    stdout.setStream(sys.stdout)
    stdout.setFormatter(stdout_fmt)

    logger.addHandler(stdout)

    if is_debug:
        logger.debug('Debug logging is enabled')
