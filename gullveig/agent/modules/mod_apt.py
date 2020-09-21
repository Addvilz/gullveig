import importlib
import logging

from gullveig.agent.lib.nativedp import has_python_library

LOGGER = logging.getLogger('gullveig-agent')


def key():
    return 'mod_apt'


def supports():
    return has_python_library('apt')


def get_report(config):
    # noinspection PyPackageRequirements
    import apt

    report = {
        'meta': {
            'upgrades': {}
        },
        'status': []
    }
    has_upgrades = False

    for pkg in apt.cache.Cache():
        if pkg.is_upgradable:
            has_upgrades = True
            try:
                report['meta']['upgrades'][pkg.fullname] = {
                    'installed': pkg.installed.version,
                    'candidate': pkg.candidate.version
                }
            except BaseException as e:
                LOGGER.error('Failed to add package to APT upgrade meta list - %s', e)

    report['status'].append({
        's': 'apt',
        't': 'upgradable',
        'r': None,
        'st': 1 if has_upgrades else 0,
        'm': False
    })

    return report
