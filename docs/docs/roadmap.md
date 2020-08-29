---
title: Platform roadmap
sidebar_label: Roadmap
---

This section documents pending changes, upcoming features and future expansion plans for Gullveig.

## Agent

### Planned architecture changes

- Detach module invocation from reporting loop, have reports gathered independently of reporting.

### Planned features

- Remote configuration - ability to receive and automatically reload configuration from reporting server.
- Ability to specify module invocation intervals per individual module. Each module report should have "expiry" time after which the report is discarded and should be no longer reported as actual.

### Planned modules

#### Near future

- mod_http - check if a remote HTTP endpoint is reachable, with timeouts and latency check.
- mod_rport - check if a remote TCP port is open, with timeouts and latency check.
- mod_lwall - verify local ports are open, and bound to expected interfaces.
- mod_cert - check if a remote HTTP certificate is valid and non-expired. Alert N hours before expiry.
- mod_iload - monitor per-interface bandwidth utilization, issue alerts on thresholds.
- mod_fail2ban - report fail2ban metrics. 

#### Later

- mod_authevent - report authentication events using `pam_exec` receiver. Depends on events feature.
- mod_snmp - SNMP query module.
- mod_oscap - monitor OpenSCAP compliance.
- mod_pdnsrec - monitor PowerDNS recursor.

## Server

- Metadata based monitoring (alert on key change, new items, etc.)
- Alerting integrations other than SMTP - Pushover, Pagerduty, Opsgenie, VictorOps, Slack.
- Automated database backups.
- Custom data retention rules.

## Web

- Improve timestamps for metric charts.
- Redesign metadata explorer.
- Health history pagination.

## Util

- Command line tool to make server forget about a node (cleanup all data).
- Command line tool to remove status items (data cleanup).
- Command line tool to mark services for scheduled downtime.

## Platform

- Support for event reporting - ability for agents to report local events remotely as a kind of "remote log". Would introduce a new section and concept in reporting - "events", with a separate section in Web. Would be useful to monitor singular events and state changes (user logins, interesting log events, etc.)
- Support for events to be marked "audit" with special storage and retention provisions.
