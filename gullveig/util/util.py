import argparse
import configparser
import os
import socket
import ssl
import sys
from getpass import getpass
from os import path

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from gullveig.common.configuration import Configuration

FILE_BASEDIR = path.dirname(__file__)
TEMPLATES_AT = path.realpath(path.join(FILE_BASEDIR, 'conf'))


def bail(message, *args):
    print(message, *args)
    exit(-1)


def pair(config):
    data_dir_cfg = config['agent']['data_dir']
    data_dir = config.resolve_config_path(data_dir_cfg)

    if not os.path.isdir(data_dir):
        return bail('Agent data directory does not exist - %s' % data_dir)

    if not os.access(data_dir, os.W_OK):
        return bail('Agent data directory is not writable - %s' % data_dir)

    server_cert_path = os.path.join(data_dir, 'server.pem')
    client_conf_path = os.path.join(data_dir, 'client.conf')

    if os.path.exists(server_cert_path) or os.path.exists(client_conf_path):
        replace = input('Configuration exists - do you want to replace existing configuration? (y)es/(n)o: ')
        replace_lc = replace.lower()
        if replace_lc != 'y' and replace_lc != 'yes':
            return bail('Not overriding existing configuration')

    def hash_readable(string, space_after):
        return ' '.join(string[i:i + space_after] for i in range(0, len(string), space_after))

    server_host = input('Server host [127.0.0.1]: ')
    if len(server_host) == 0:
        server_host = '127.0.0.1'

    server_port = input('Server port [8765]: ')
    if len(server_port) == 0:
        server_port = 8765
    else:
        if not server_port.isnumeric():
            print('Server port is not valid, expected number')
        server_port = int(server_port)
        if server_port < 1 or server_port > 65535:
            print('Server port is not valid, expected in range 1-65535')

    server_key = getpass('Server key: ')
    if len(server_key) == 0:
        return bail('Server key not provided, terminating')

    print('Retrieving certificate for %s:%s' % (server_host, server_port))
    try:
        cert = ssl.get_server_certificate((server_host, server_port))
    except ssl.SSLError:
        return bail('Failed to obtain server certificate, verify hostname and port number of the server and try again.')
    except socket.gaierror as e:
        return bail('Failed to obtain server certificate - %s' % e)
    except ConnectionRefusedError:
        return bail('Failed to connect to server, verify the server is running and accessible from this host.')

    try:
        cx = x509.load_pem_x509_certificate(cert.encode(), default_backend())
    except BaseException as e:
        print(e)
        return bail('Failed to parse remote certificate')

    print('\n' + ('-' * 80))
    print('ISSUED BY : %s' % cx.issuer.rfc4514_string())
    print('ISSUED TO : %s' % cx.subject.rfc4514_string())
    print('ISSUED    : %s' % cx.not_valid_before)
    print('EXPIRES   : %s' % cx.not_valid_after)
    print('SHA1      : %s' % hash_readable(cx.fingerprint(hashes.SHA1()).hex(), 4))
    print('SHA256:   : %s' % hash_readable(cx.fingerprint(hashes.SHA256()).hex(), 4))
    print(('-' * 80) + '\n')

    print('IMPORTANT: Please, verify the above information is valid and matches the certificate issued to '
          ' your Gullveig server.\n')

    answer = input('Is above information correct? Type "confirm" to continue: ')

    if answer != 'confirm':
        return bail('Not confirming, terminating.')

    print('Writing server certificate to %s' % server_cert_path)

    with open(server_cert_path, 'w') as file:
        file.write(cert)

    client_conf = configparser.ConfigParser()
    client_conf['client'] = {
        'server_host': server_host,
        'server_port': str(server_port),
        'client_key': server_key,
    }

    print('Writing client configuration and credentials to %s' % client_conf_path)
    with open(client_conf_path, 'w') as file:
        client_conf.write(file)

    print('Pairing complete! You can now start the Gullveig agent.')


def main():
    parser = argparse.ArgumentParser(
        description='Gullveig reporting utilities',
        usage='''gullveig-util <command> [<args>]
        
Available commands:
    pair    Pair Gullveig agent and server
        '''
    )
    parser.add_argument('command', help='Command to execute')

    args = parser.parse_args(sys.argv[1:2])

    if 'pair' == args.command:
        sub_parser = argparse.ArgumentParser(description='Pair Gullveig agent and server')
        sub_parser.add_argument(
            '--config',
            help='Agent configuration file, defaults to /etc/gullveig/agent.conf',
            default='/etc/gullveig/agent.conf'
        )

        sub_args = sub_parser.parse_args(sys.argv[2:])
        config = Configuration(sub_args.config, {
            'agent': {
                'data_dir': '/var/lib/gullveig'
            }
        })

        if not config.is_file_path_valid():
            return bail('Configuration file is not readable - %s', sub_args.config)

        config.initialize()

        pair(config)
        return

    bail('Unknown command - %s' % args.command)
