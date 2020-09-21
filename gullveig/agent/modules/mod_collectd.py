import fnmatch
import logging
import socket
from datetime import datetime
from typing import List, Optional

from gullveig.agent.modules import get_resource_threshold_exceeded

LOGGER = logging.getLogger('gullveig-agent')


class Collectd:
    def __init__(self, socket_path: str):
        self.socket_path = socket_path
        self.socket = self.create_socket()

    def __del__(self):
        if not self.socket:
            return

        try:
            self.socket.close()
        except BaseException as e:
            LOGGER.debug('Failed to close collectd socket', exc_info=e)
            pass

    def ensure(self) -> bool:
        if not self.socket:
            self.socket = self.create_socket()
        return self.socket is not None

    def create_socket(self) -> socket:
        socket_instance = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        socket_instance.settimeout(1)
        try:
            socket_instance.connect(self.socket_path)
        except BaseException as e:
            LOGGER.debug('Failed to open collectd socket', exc_info=e)
            return None

        return socket_instance

    def list_values(self) -> List[str]:
        expect_values = self.raw_command('LISTVAL')

        if not expect_values:
            return []

        return self.read_lines(expect_values)

    def raw_command(self, cmd: str) -> int:
        self.socket.send(('%s\n' % cmd).encode('ASCII'))

        status_message = self.read_line()

        if not status_message:
            return 0

        code, message = status_message.split(' ', 1)

        if int(code):
            return int(code)

        return 0

    def read_lines(self, number_of_lines) -> List[str]:
        buffer = []
        while True:
            line = self.read_line()

            if not line:
                break

            buffer.append(line)

            if number_of_lines and len(buffer) >= number_of_lines:
                break

        return buffer

    def read_line(self) -> str:
        buffer = []

        while True:
            data = self.socket.recv(1)

            if data == b'\n':
                break

            buffer.append(data.decode('ASCII'))

        return (''.join(buffer)).strip()

    def get_value(self, item_identifier: str) -> Optional[List[str]]:
        expect_values = self.raw_command('GETVAL "%s"' % item_identifier)

        if not expect_values or expect_values < 0:
            return None

        return self.read_lines(expect_values)


def key():
    return 'mod_collectd'


def supports():
    return True


def get_report(config):
    report = {
        'metric': [],
        'status': []
    }

    sock = config['mod_collectd']['socket']
    value_conf = config['mod_collectd_values']

    value_conf_map = {}
    for (conf_key, conf_val) in value_conf.items():
        options = conf_val.split(' ')

        if len(options) != 4:
            LOGGER.error(
                'Configuration malformed: mod_collectd_values, key "%s", value "%s", expected 4 options, got %d.',
                conf_key,
                conf_val,
                len(options)
            )
            continue

        (status, warn_at, critical_at, data_format) = options

        match_status = status.lower()

        value_conf_map[conf_key] = {
            'status': True if (match_status == 'yes' or match_status == 'true') else False,
            'warn_at': None if '-' == warn_at else float(warn_at),
            'critical_at': None if '-' == critical_at else float(critical_at),
            'format': data_format
        }

    collectd = Collectd(sock)
    is_connected = collectd.ensure()

    if not is_connected:
        LOGGER.warning('Collectd socket can not be connected to, ignoring')
        return None

    collectd_values = collectd.list_values()

    now = datetime.now().timestamp()

    for collectd_value in collectd_values:
        timestamp, item = collectd_value.split()

        age_seconds = now - float(timestamp)
        old_record = age_seconds > 300  # Records older than 5 minutes ignored

        values = collectd.get_value(item)

        for value in values:
            (key, num) = value.split('=', 2)

            if old_record:
                f_value = 0
            elif num == 'NaN':
                f_value = 0
            else:
                f_value = float(num)

            if key == 'value':
                full_key = item
            else:
                full_key = '%s/%s' % (item, key)

            (_, subject, metric) = full_key.split('/', 2)

            entry_key = '/%s/%s' % (subject, metric)
            record_spec = None

            for (match_key, spec) in value_conf_map.items():
                if not fnmatch.fnmatch(entry_key, match_key):
                    continue
                record_spec = spec
                break

            if record_spec is None:
                continue

            # Normalize the entry display values
            metric_name = metric
            if metric.startswith(subject + '-'):
                metric_name = metric[len(subject) + 1:]

            if metric.startswith(subject + '_'):
                metric_name = metric[len(subject) + 1:]

            if metric.startswith(subject + '/'):
                metric_name = metric[len(subject) + 1:]

            warn_at = record_spec['warn_at']
            critical_at = record_spec['critical_at']

            report['metric'].append({
                's': subject,
                'm': metric_name,
                'v': f_value,
                'f': 0,
                't': 0 if critical_at is None else critical_at,
                'd': record_spec['format']
            })

            if not record_spec['status']:
                continue

            status = 0
            if warn_at is not None and f_value > warn_at:
                status = 1
            if critical_at is not None and f_value > critical_at:
                status = 2

            report['status'].append({
                's': subject,
                't': metric_name,
                'r': get_resource_threshold_exceeded(critical_at, f_value),
                'st': status,
                'm': True
            })

    return report
