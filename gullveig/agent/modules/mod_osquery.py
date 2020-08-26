import importlib
import logging
from os import path

import yaml

from gullveig.agent.modules import get_resource_threshold_exceeded

LOGGER = logging.getLogger('gullveig-agent')


def parse_str_as_number(str_value):
    if '.' in str_value:
        return float(str_value)

    return int(str_value)


def key():
    return 'mod_osquery'


def supports():
    if not hasattr(importlib, 'util'):
        spec = importlib.find_loader('osquery')
    else:
        spec = importlib.util.find_spec('osquery')

    return spec is not None


def get_report(config):
    # noinspection PyPackageRequirements
    import osquery

    report = {
        'meta': {},
        'status': [],
        'metric': []
    }

    mod_conf = config['mod_osquery']['config']
    mod_conf_path = config.resolve_config_path(mod_conf)

    if not path.isfile(mod_conf_path):
        LOGGER.error('mod_osquery - configuration file is not a file')
        return

    with open(mod_conf_path, 'r') as mod_conf_res:
        try:
            osquery_conf = yaml.load(mod_conf_res, Loader=yaml.FullLoader)
        except BaseException as e:
            LOGGER.exception('Failed to read osquery configuration file', e)
            return

    instance = osquery.SpawnInstance()
    try:
        instance.open(timeout=0.02)
    except BaseException as e:
        LOGGER.exception('Failed to connect to osquery', e)
        return

    client = instance.client

    if 'meta' in osquery_conf:
        for meta_item, query in osquery_conf['meta'].items():
            result = client.query(query)

            if result.status.code != 0:
                LOGGER.error(
                    'osquery meta query failed - %d %s, for %s',
                    result.status.code, result.status.message, query
                )

                report['meta'][meta_item] = {
                    'code': result.status.code,
                    'error': result.status.message
                }
                continue

            report['meta'][meta_item] = result.response

    if 'metrics' in osquery_conf:
        for metric, options in osquery_conf['metrics'].items():
            result = client.query(options['query'])

            if result.status.code != 0:
                LOGGER.error(
                    'osquery metric query failed - %d %s, for %s',
                    result.status.code, result.status.message, options['query']
                )
                continue

            data = result.response

            for item in data:
                report['metric'].append({
                    's': item['subject'],
                    'm': item['metric'],
                    'v': item['value'],
                    'f': item['from'],
                    't': item['to'],
                    'd': None if not item['format'] else item['format']
                })

    if 'status' in osquery_conf:
        for status, options in osquery_conf['status'].items():
            result = client.query(options['query'])

            if result.status.code != 0:
                LOGGER.error(
                    'osquery status query failed - %d %s, for %s',
                    result.status.code, result.status.message, options['query']
                )
                continue

            data = result.response

            if len(data) == 0:
                # Nothing reported, state is UNKNOWN
                report['status'].append({
                    's': options['subject'],
                    't': options['type'],
                    'r': 0,
                    'st': 3,
                    'm': options['is_metric']
                })
                continue

            warning_at = options['threshold']['warning']
            critical_at = options['threshold']['critical']

            str_value = data[0]['value']
            try:
                value = parse_str_as_number(str_value)
            except ValueError as e:
                LOGGER.exception('Failed to parse value %s as number', str_value, e)
                continue

            resource = None

            if 'resource' in data[0]:
                try:
                    resource = parse_str_as_number(data[0]['resource'])
                except ValueError as e:
                    LOGGER.exception('Failed to parse value %s as number', data[0]['resource'], e)
                    continue

            if value >= critical_at:
                state = 2
                if resource is None:
                    resource = get_resource_threshold_exceeded(critical_at, value)
            elif value >= warning_at:
                state = 1
                if resource is None:
                    resource = get_resource_threshold_exceeded(critical_at, value)
            else:
                state = 0
                if resource is None:
                    resource = get_resource_threshold_exceeded(critical_at, value)

            report['status'].append({
                's': options['subject'],
                't': options['type'],
                'r': resource,
                'st': state,
                'm': options['is_metric']
            })

    return report
