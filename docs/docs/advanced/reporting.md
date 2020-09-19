---
title: Reporting internals
sidebar_label: Reporting
---

## Module report cache and expiry

Version 0.1.16 introduces cached status reporting. Using [agent configuration](../configuration/agent.conf.md)
keys `fetch_every` and `expires_after` it is now possible to control module execution timing separately from
report submission timing.

Internally, Gullveig agents will preserve the last report in memory and report the health status portion
of the report to the reporting server with every reporting interval as if the status would be actual.

To prevent modules from silently failing, `expires_after` is used to indicate the validity period of each
stored report. If a report becomes stale, status of such a stale report will no longer be reported to the
server and health checks will fail.

[`expires_after`](../configuration/agent.conf.md#_expires_after) should be reasonably long to prevent reports expiring
in the middle of the module execution cycle.

A good example of how to determine a good expiry time is - if the `fetch_every` is set to 60 seconds, 
and module spends 30 seconds gathering data, `expires_after`
should be no less than `(report_delay * tolerance) + (60 + 30)` seconds, where `tolerance` is the number of 
reporting cycles you would like for the report cache to survive.
