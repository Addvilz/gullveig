---
title: Monitoring
sidebar_label: Monitoring
---

Gullveig allows for remote service and resource monitoring. This is implemented using various
[default modules](../modules/overview.md) and can be extended with [custom modules](../advanced/extending.md).

## Monitoring using agents

Gullveig is a remote monitoring platform and uses agents installed to target systems to monitor the state
of the resources and services on said systems.

You can also use [virtual agents](../advanced/monitoring.md) to monitor systems and resources
where agent installation is impossible or not recommended.

## How does it work?

Each deployed agent gathers information about the host system and services using configured modules.
The state of the system is then reported to the Gullveig reporting server.

Gullveig reporting server stores all incoming data in local database, analyzes it and reports any anomalies
reported by the agents.

Reporting server will also alert you if for any reason some status reports or updates
are no longer received - which could indicate failure in agent itself, the agent host or services being monitored.

When an alert condition is encountered, Gullveig reporting server will dispatch an aggregate message listing
actual failures since last reported state. When possible, reporting server will group multiple alerts together
as to not overwhelm the operations with redundant notifications.

## Resource monitoring

In addition to raw status, agents also report metrics - a point-in-time observations of countable resources. You
can view time series graphs of the metrics reported by agents in the web user interface.

All metrics collected by agents are point-in-time and report values at the time of observation. Metrics
are aggregated and viewable grouping by second, minute, hour, day, week, month and year of observation.

Metrics aggregate minimum, average and maximum values for each time period, and will graph the observations
accordingly.
