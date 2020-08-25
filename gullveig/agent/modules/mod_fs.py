import logging

import psutil

from gullveig.agent.modules import get_int_marker_for_percentage, get_resource_remaining_percent

LOGGER = logging.getLogger('gullveig-agent')


def key():
    return 'mod_fs'


def supports():
    return True


def get_report(config):
    ignore_read_only = config['mod_fs'].getboolean('ignore_ro')

    report = {
        'meta': {
            'mount': {}
        },
        'metric': [],
        'status': []
    }

    for partition in psutil.disk_partitions():
        part_options = partition.opts.split(',')
        is_squashfs = 'squashfs' == partition.fstype
        is_readonly = 'ro' in part_options

        # There is nothing to monitor about squashfs
        if is_squashfs:
            LOGGER.debug('Ignoring mount %s - it is of type squashfs', partition.mountpoint)
            continue

        # Should ignore read only?
        if is_readonly and ignore_read_only:
            LOGGER.debug('Ignoring read only mount %s, ignore_ro flag set', partition.mountpoint)
            continue

        usage = psutil.disk_usage(partition.mountpoint)

        report['meta']['mount'][partition.mountpoint] = {
            'dev': partition.device,
            'type': partition.fstype,
            'opt': partition.opts,
        }

        report['metric'].append({
            's': partition.mountpoint,
            'm': 'used',
            'v': usage.used,
            'f': 0,
            't': usage.total,
            'd': 'b'
        })

        percent_available = get_resource_remaining_percent(usage.used, usage.total)

        report['status'].append({
            's': partition.mountpoint,
            't': 'used',
            'r': percent_available,
            'st': get_int_marker_for_percentage(percent_available, 10, 5),
            'm': True
        })

    return report
