import logging

from gullveig import bootstrap_default_logger


# Configure default logging
def _configure_default_web_logger():
    logger = logging.getLogger('gullveig-web')
    bootstrap_default_logger(logger)

    api_logger = logging.getLogger('gullveig-api')
    bootstrap_default_logger(api_logger)

    aio_logger = logging.getLogger('aiohttp.server')
    bootstrap_default_logger(aio_logger)


_configure_default_web_logger()
