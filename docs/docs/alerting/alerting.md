---
title: Alerting
sidebar_label: Alerting
---

Gullveig platform continuously monitors service and resource health. When resource thresholds are met, Gullveig
server will issue health alerts to inform about changes in service conditions.

When enabled, Gullveig agent modules will report service state directly to the server. If the state changes,
the server will issue alerts reporting what services changed on what nodes. Service state is verified once every 
10 seconds. When possible, multiple state changes will be bundled in a single notification.

For service specific alerts, consult documentation of each individual module.

## Internal alerts related to platform health

Gullveig agents will issue internal health alerts when agent is unable to connect to the reporting server - by default,
after 120 seconds of continuous downtime. This is to ensure redundancy in case reporting server is offline or 
not reachable for any reason.

Gullveig server will periodically check last time status was reported on per agent basis. When
service reporting timeout exceeds, by default, 120 seconds, the server will change state of all related services
to UNKNOWN and issue an alert. This is to safeguard against cases when agents go absent or stop reporting state
of one or more services.

When restarted, Gullveig server will wait for up to 10 minutes for all agents to reconnect and report their state.
Once this grace period lapses, server will consider all the agents missing and will mark all the related missing services
as UNKNOWN.
