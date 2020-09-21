---
title: mod_collectd
sidebar_label: mod_collectd
---

**Introduced in version:** 0.1.20

## About

This module monitors and alerts on values exposed by [collectd](https://collectd.org) system statistics 
collection daemon. 

collectd offers [number of useful plugins](https://collectd.org/wiki/index.php/Table_of_Plugins) that
allow for ingest of detailed metrics for many popular services, such as NGINX, OpenVPN, libvirt, and more.

This module is designed to work with non-networked collectd instances.

## System requirements

- `collectd` must be installed, configured and running.
- `collectd` must NOT be configured as multihost server.

## collectd configuration

For the integration to work, you must expose collectd UNIX socket to Gullveig using collectd 
[UnixSock plugin](https://collectd.org/wiki/index.php/Plugin:UnixSock).

1. Load `unixsock` plugin by uncommenting this line:

```
LoadPlugin unixsock
```

2. Configure `unixsock` plugin to expose unix socket. Ensure that `SocketGroup` option is set to the group Gullveig
agent service is using.

```
<Plugin unixsock>
	SocketFile "/var/run/collectd-unixsocket-gullveig"
	SocketGroup "GULLVEIG_USER"
	SocketPerms "0660"
	DeleteSocket false
</Plugin>
```

## Alerts

This module will issue alerts if configured to do so on per-metric basis.

## Metadata

None.

## Metrics

This module will report all configured collectd metrics to Gullveig.

**Note:** collectd metrics that have not been updated for longer than 5 minutes will have their values set to `0`.

## Configuration

### Section [mod_collectd]

#### socket
**Default value:** `/var/run/collectd-unixsocket-gullveig`

Path to collectd UNIX socket.

### Section [mod_collectd_values]

This section configures metric matching for metrics to be read by Gullveig from collectd.
All entries are key value pairs of follwing format

```
PATTERN = REPORT_STATUS_BOOL WARN_THRESHOLD CRIT_THRESHOLD DATA_FORMAT
```

#### PATTERN

A Unix shell-style pattern to match the value exposed by collectd. Uses [fnmatch](https://docs.python.org/3/library/fnmatch.html)
to match the pattern against values exposed by collectd.

All collectd items have hostname removed and start with forward-slash, for example - `/memory/memory-buffered`,
`/memory/memory-free`.

> **NOTE** avoid greedy pattern matches, such as `/*`. Only export metrics you actually intend to use.

#### REPORT_STATUS_BOOL

Boolean like value (`true`, `false`, `yes`, `no`) to indicate whether or not status monitoring should be 
enabled for this metric. When disabled, metric will be reported without an accompanying status entry.

#### WARN_THRESHOLD

When REPORT_STATUS_BOOL is truthy, this value can contain value, exceeding which the status
of this metric will enter INCIDENT state.

Use single dash (`-`) to indicate no value.

#### CRIT_THRESHOLD

When REPORT_STATUS_BOOL is truthy, this value can contain value, exceeding which the status
of this metric will enter CRITICAL state.

Use single dash (`-`) to indicate no value.

#### DATA_FORMAT

Data format - `b` for bytes, `%` for percentage. You can use any unit here, other than
`b` and `%` will be shown in the UI as-is.

### Example configuration

```ini
[mod_collectd]
socket = /var/run/collectd-unixsocket-gullveig

[mod_collectd_values]
# Report and alert on used swap
/swap/swap-used = yes 125056600 155056600 b

# Report all items that start with /load/
/load/* = no - - -
```
