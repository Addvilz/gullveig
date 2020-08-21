import logging
import shutil
import subprocess

from gullveig.agent.modules import StatusMarker

LOGGER = logging.getLogger('gullveig-agent')


def key():
    return 'mod_systemd'


def supports():
    return shutil.which('systemctl') is not None


def get_state_for_service(service):
    cmd = ['systemctl', 'show', '--no-page', '--property=ActiveState', service]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
    except BaseException as e:
        LOGGER.error('mod_systemd failed to execute systemctl for service %s, %s', e)
        return None

    if 0 is not result.returncode:
        LOGGER.error(
            'mod_systemd failed to execute systemctl, exit code %d for service %s',
            result.returncode,
            service
        )
        return None

    return result.stdout[12:-1].decode('ascii')


def get_report(config):
    report = {
        'status': []
    }

    if 'mod_systemd' not in config:
        return {}

    for service, state in config['mod_systemd'].items():
        real_state = get_state_for_service(service)
        if real_state is None:
            continue  # Can't tell, skip

        status = StatusMarker.OK if real_state == state else StatusMarker.CRITICAL

        report['status'].append({
            's': service,
            't': state,
            'r': None,
            'st': status.value,
            'm': False
        })

    return report
