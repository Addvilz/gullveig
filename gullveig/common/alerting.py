from datetime import datetime
from email.message import EmailMessage
from logging import Logger

import aiosmtplib

from gullveig.common.configuration import Configuration


class FailureObserver:
    def __init__(self, logger: Logger) -> None:
        self.cause = None
        self.logger = logger
        self.since = None
        self.handled = False

    def reset(self) -> None:
        self.cause = None
        self.since = None
        self.handled = False
        self.logger.debug('Failure observer reset')

    def mark_handled(self) -> None:
        self.handled = True
        self.logger.debug('Failure observer handled')

    def mark_failure(self, cause=None) -> None:
        if self.since is not None:
            return
        self.cause = cause
        self.since = datetime.now()
        self.logger.debug('Failure observer marked')

    def not_handled_for_more_than(self, limit_seconds: int) -> bool:
        if self.since is None or self.handled:
            return False

        diff = datetime.now() - self.since

        return diff.total_seconds() > limit_seconds


def status_to_name(status: int) -> str:
    if status == 0:
        return 'OK'
    elif status == 1:
        return 'INCIDENT'
    elif status == 2:
        return 'OUTAGE'
    elif status == 3:
        return 'UNKNOWN'


class AlertManager:
    def __init__(self, config: Configuration, logger: Logger) -> None:
        """
        :type config: Configuration Server OR Agent configuration
        """
        self.config = config
        self.enabled = config['mail'].getboolean('enabled')
        self.logger = logger
        self.agent_server_comm_last = None

    async def dispatch_server_alerts(self, alerts: list) -> None:
        if not self.enabled:
            self.logger.debug('Not sending health notification - email disabled')
            return

        statuses = [alert['status'] for alert in alerts]
        max_status = max(statuses)

        if max_status == 0:
            overall = 'NOMINAL'
        elif max_status == 1:
            overall = 'INCIDENT'
        elif max_status == 2:
            overall = 'OUTAGE'
        elif max_status == 3:
            overall = 'OUTAGE'
        else:
            raise RuntimeError('Unknown status')

        try:
            sender = self.config['mail']['smtp_from']
            subject = '[GULLVEIG] Service status has changed to %s' % overall

            text = 'Service state has changed: \n\n'

            for alert in alerts:
                alert['status'] = status_to_name(alert['status'])
                alert['before'] = status_to_name(alert['before'])
                alert['updated_at'] = datetime.fromtimestamp(alert['updated_at'] / 1000)

                text += '- {ident} {mod} {subject} {type}, current state is {status}, was {before}'.format(**alert)

                if alert['remaining']:
                    text += ', reported value {remaining}'.format(**alert)

                text += ', reported at {updated_at}\n\n'.format(**alert)

            text += '\nThis is an automated status notification sent by Gullveig server.'

            await self.send_mail(sender, subject, text)
        except BaseException as e:
            self.logger.error('Failed to send email notification - %s', e)

    async def on_agent_server_comm_failure(self, cause) -> None:
        if not self.enabled:
            self.logger.debug('Not sending server connection failure notification - email disabled')
            return

        # Send alert no more than once per hour to prevent agent alert flood
        if self.agent_server_comm_last is not None:
            diff = datetime.now() - self.agent_server_comm_last
            if diff.total_seconds() < 3600:
                self.logger.debug('Not sending server connection failure notification - email grace period')

        try:
            cause_txt = 'Error details: %s.' % ('unknown error' if cause is None else str(cause))

            ident = self.config['agent']['ident']
            sender = self.config['mail']['smtp_from']
            subject = '[GULLVEIG] Reporting server unreachable from %s' % ident
            text = 'The agent with ident "%s" is unable to reach the configured Gullveig reporting server.' \
                   '\n\n' \
                   '%s' \
                   '\n\n' \
                   'This is an automated status notification sent by Gullveig agent.' % (ident, cause_txt)

            await self.send_mail(sender, subject, text)

            self.agent_server_comm_last = datetime.now()

            self.logger.debug('Sent alert about server connection failure')
        except BaseException as e:
            self.logger.error('Failed to send email notification - %s', e)

    async def send_mail(self, sender, subject, text) -> None:
        message = EmailMessage()
        message['From'] = sender
        message['To'] = ','.join(self.config['mail']['smtp_to'].split(' '))
        message['Subject'] = subject
        message.set_content(text)

        use_tls = False
        use_starttls = False

        mode = self.config['mail']['smtp_mode']

        if mode == 'tls':
            use_tls = True
            use_starttls = False
        elif mode == 'starttls':
            use_tls = False
            use_starttls = True

        await aiosmtplib.send(
            message=message,
            hostname=self.config['mail']['smtp_host'],
            port=self.config['mail'].getint('smtp_port'),
            username=self.config['mail']['smtp_user'],
            password=self.config['mail']['smtp_password'],
            use_tls=use_tls,
            start_tls=use_starttls
        )
