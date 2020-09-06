import logging
from socket import AddressFamily

import psutil

from gullveig.agent.modules import StatusMarker

LOGGER = logging.getLogger('gullveig-agent')


class Interface:
    def __init__(self, iface: str, port: int, family: AddressFamily) -> None:
        self.iface = iface
        self.port = port
        self.any = False
        self.loopback = False
        self.ipv4 = False
        self.ipv6 = False
        self.family = None

        if family is AddressFamily.AF_INET6:
            self.family = 'IPv6'
            self.ipv6 = True

            if '::ffff:' == iface[0:7]:
                self.ipv4 = True
                self.family = 'IPv4/6'

            if '::ffff:127.0.0.1' == iface:
                self.loopback = True
                return
            if '::1' == iface:
                self.loopback = True
                return
            if '::' == iface:
                self.any = True
            return

        if family is AddressFamily.AF_INET:
            self.family = 'IPv4'
            self.ipv4 = True

            if '127.0.0.1' == iface:
                self.loopback = True
                return
            if '0.0.0.0' == iface:
                self.any = True
            return

        raise RuntimeError('Unsupported address family - %s' % family)

    def match_val(self) -> str:
        if self.any:
            return 'any'

        if self.loopback:
            return 'loopback'

        return self.iface

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class InterfaceList(list):
    def all_loopback(self) -> bool:
        for iface in self:
            if not iface.loopback:
                return False

        return True

    def all_any(self) -> bool:
        for iface in self:
            if not iface.loopback:
                return False

        return True


def key():
    return 'mod_lwall'


def supports():
    return True


def get_report(config):
    try:
        net_connections = psutil.net_connections(kind='inet')
    except BaseException as e:
        LOGGER.exception('Failed to acquire network connection list', e)
        return {}

    policy_any = config['mod_lwall']['policy_any']
    policy_loopback = config['mod_lwall']['policy_loopback']
    policy_bound = config['mod_lwall']['policy_bound']

    port_policy = {}

    for port, policy in config['mod_lwall_map'].items():
        port_policy[int(port)] = policy.split(' ')

    ports = {}

    for (_, family, _, local, _, status, _) in net_connections:
        if 'LISTEN' != status:
            continue

        (local_iface, local_port) = local

        local_port = int(local_port)

        if local_port not in ports:
            ports[local_port] = InterfaceList()

        ports[local_port].append(Interface(local_iface, local_port, family))

    violations = []

    # Ports in policy that are not bound
    for c_port, c_policy in port_policy.items():
        if c_port in ports:
            continue

        violations.append({
            'port': c_port,
            'family': None,
            'policy': c_policy,
            'violation': 'is_closed'
        })

    for l_port, l_interfaces in ports.items():
        if l_port not in port_policy:
            for l_interface in l_interfaces:
                if not l_interface.any and not l_interface.loopback and policy_bound == 'allow':
                    continue
                if l_interface.any and policy_any == 'allow':
                    continue
                if l_interface.loopback and policy_loopback == 'allow':
                    continue

                violations.append({
                    'port': l_port,
                    'family': l_interface.family,
                    'policy': None,
                    'violation': 'is_open'
                })
            continue

        policies = port_policy[l_port]
        matched_policies = {}

        for l_interface in l_interfaces:
            match_val = l_interface.match_val()
            if match_val in policies:
                matched_policies[match_val] = True
                continue

            violations.append({
                'port': l_port,
                'family': l_interface.family,
                'policy': policies,
                'violation': 'is_' + match_val
            })

        for policy in policies:
            if policy in matched_policies:
                continue

            violations.append({
                'port': l_port,
                'family': None,
                'policy': policies,
                'violation': 'is_' + policy
            })

    violations.sort(key=lambda it: (it['port'], str(it['family']), it['violation']))

    port_meta = {}

    for port, interfaces in ports.items():
        i_list = []
        for interface in interfaces:
            i_list.append({
                'iface': interface.iface,
                'port': interface.port,
                'any': interface.any,
                'loopback': interface.loopback,
                'ipv4': interface.ipv4,
                'ipv6': interface.ipv6,
                'family': interface.family,
            })

        port_meta[port] = i_list

    status = StatusMarker.OK if 0 == len(violations) else StatusMarker.CRITICAL

    report = {
        'meta': {
            'violations': violations,
            'ports': port_meta
        },
        'status': [
            {
                's': 'ports',
                't': 'policy',
                'r': None,
                'st': status.value,
                'm': False
            }
        ]
    }

    return report
