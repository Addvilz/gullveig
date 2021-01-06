---
title: Platform roadmap
sidebar_label: Roadmap
---

This section documents pending changes, upcoming features and future expansion plans for Gullveig.

Please, open a ticket or comment on existing ticket before working on any code changes to avoid code conflicts and
to confirm that your changes can be incorporated in the codebase before spending time implementing them.

See the [contributions policy](https://github.com/Addvilz/gullveig/blob/master/CONTRIBUTING.md) for more information.

## Agent

### Planned features

- Migrating to complete remote configuration using node groups - agents will receive configuration from the server, exclusively.
- Drop support for WebSockets as event transport.
- Performance optimizations.

### Planned modules

#### Near future

- mod_http - check if a remote HTTP endpoint is reachable, with timeouts and latency check.
- mod_rport - check if a remote TCP port is open, with timeouts and latency check.
- mod_cert - check if a remote HTTP certificate is valid and non-expired. Alert N hours before expiry.
- mod_ifload - monitor per-interface bandwidth utilization, issue alerts on thresholds.

#### Later

- mod_pkg_cve - check installed packages against CVE vulnerabilities.
- mod_authevent - report authentication events using `pam_exec` receiver. Depends on events feature.
- mod_snmp - SNMP query module.
- mod_oscap - monitor OpenSCAP compliance.
- mod_pdnsrec - monitor PowerDNS recursor.
- mod_fail2ban - report fail2ban metrics.

## Server

- Dropping support for SQLite and replacing it with a standalone database server.
- Metadata based monitoring (alert on key change, new items, etc.)
- Alerting integrations other than SMTP - Pushover, Pagerduty, Opsgenie, VictorOps, Slack.
- Custom data retention rules.
- Performance optimizations.

## Web

- Improve timestamps for metric charts.
- Health history pagination.
- Redesign graphs and charts.

## Util

- Command line tool to make server forget about a node (cleanup all data).
- Command line tool to remove status items (data cleanup).
- Command line tool to mark services for scheduled downtime.

## Platform

- Support for event reporting - ability for agents to report local events remotely as a kind of "remote log". Would introduce a new section and concept in reporting - "events", with a separate section in Web. Would be useful to monitor singular events and state changes (user logins, interesting log events, etc.)
- Support for events to be marked "audit" with special storage and retention provisions.
- Support for "canary" events - expectation for certain events to be invoked on certain intervals. Failure to send an event will trigger an alert. 
