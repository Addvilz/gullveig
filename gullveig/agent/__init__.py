import logging
import ssl
from asyncio import base_events

from gullveig import bootstrap_default_logger

# Compat with < 3.7
if hasattr(ssl, 'SSLCertVerificationError'):
    base_events._FATAL_ERROR_IGNORE = ssl.SSLCertVerificationError


def _configure_default_agent_logger():
    logger = logging.getLogger('gullveig-agent')
    bootstrap_default_logger(logger)


_configure_default_agent_logger()
