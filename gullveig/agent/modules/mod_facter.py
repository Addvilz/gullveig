import json
import logging
import shutil
import subprocess

LOGGER = logging.getLogger('gullveig-agent')


def key():
    return 'mod_facter'


def supports():
    return shutil.which('facter') is not None


def get_report(config):
    cmd = ['facter', '-j']

    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if 0 is not result.returncode:
        LOGGER.warning('mod_facter failed to execute, exit code %d. Will continue regardless.', result.returncode)
        return {}

    return {
        'meta': json.loads(result.stdout)
    }
