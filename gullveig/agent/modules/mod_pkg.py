import logging

from gullveig.agent.lib.package import get_package_manager

LOGGER = logging.getLogger('gullveig-agent')


def key():
    return 'mod_pkg'


def supports():
    return True


def get_report(config):
    warn_on_upgrade = config['mod_pkg'].getboolean('upgrade_warn')

    manager = get_package_manager()

    report = {
        'meta': {
            'upgradable': []
        }
    }

    has_upgrades = False

    for pkg in manager.list_packages(limit_upgradable=True):
        has_upgrades = True
        report['meta']['upgradable'].append({
            'origin': str(pkg.origin.name),
            'name': pkg.name,
            'version': pkg.version,
            'latest': pkg.latest,
            'origin_ref': pkg.origin_ref,
            'license': 'Unknown' if pkg.license is None else pkg.license,
            'summary': None if len(str(pkg.summary)) == 0 else pkg.summary,
            'url': None if len(str(pkg.url)) == 0 else pkg.url,
        })

    if warn_on_upgrade:
        report['status'] = [{
            's': 'packages',
            't': 'upgradable',
            'r': None,
            'st': 1 if has_upgrades else 0,
            'm': False
        }]

    return report
