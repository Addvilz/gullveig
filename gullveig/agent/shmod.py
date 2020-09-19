import json
import logging
import os
import subprocess

LOGGER = logging.getLogger('gullveig-agent')


def invoke_external_module(module):
    cmd = module['cmd'].split()

    LOGGER.debug('Invoking internal module %s', module['id'])

    if len(cmd) == 0:
        raise RuntimeError('Empty command for module %s' % module['id'])

    if not os.path.isfile(cmd[0]):
        raise RuntimeError('Module file is not a file - %s' % cmd[0])

    if not os.access(cmd[0], os.X_OK):
        raise RuntimeError('Module file can not be executed - %s' % cmd[0])

    result = subprocess.run(cmd, stdout=subprocess.PIPE)

    if 0 is not result.returncode:
        raise RuntimeError('Module run failed - non-zero exit code for %s [%d]' % (module['file'], result.returncode))

    return {
        'module': module['id'],
        'report': json.loads(result.stdout)
    }


def create_external_mod(name, file):
    return {
        'id': name,
        'cmd': file,
        'external': True
    }
