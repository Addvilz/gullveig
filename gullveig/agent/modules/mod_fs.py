import psutil

from gullveig.agent.modules import StatusMarker, get_int_marker_for_percentage, get_resource_remaining_percent


def key():
    return 'mod_fs'


def supports():
    return True


def get_report(config):
    report = {
        'meta': {
            'mount': {}
        },
        'metric': [],
        'status': []
    }

    for partition in psutil.disk_partitions():
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
