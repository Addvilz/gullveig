---
title: agent.conf
sidebar_label: agent.conf
---

Gullveig agent configuration reference.

## Module configuration

Besides sections to configure agent, `agent.conf` may also contain sections related to module configuration.

Module configuration section names are identical to the module they refer to, for example,
a section for `mod_fs` would be `[mod_fs]`.

For simple deployments module configuration sections should be placed in `agent.conf` directly. For
complex deployments, you can use `agent.conf.d` directory and create a file for each module separately. Refer to [this section](./about.md#compartmentalizing-complex-configuration) of the configuration manual for more information.

## Section [agent]

### ident
**Default value:** reverse FQDN of the host where agent is installed.

Unique identifier of this agent node.

### data_dir
**Default value:** `/var/lib/gullveig/`

Agent data directory. This directory contains agent credentials and files related to
communicating to the server.

### mod_workers
**Default value:** number of CPU cores on the system divided by two, but no less than 1.

Number of workers to use to gather information.

### report_delay
**Default value:** `5`

Seconds to wait between sending reports.

### reconnect_delay
**Default value:** `10`

Seconds to wait between reattempting to reconnect to reporting server when a connection is lost or interrupted.

### server_ko_grace
**Default value:** `120`

Approximate delay, in seconds, between when a server connection is lost and alert is dispatched notifying that agent is no longer able to connect to the reporting server.

### ping_timeout
**Default value:** `1`

Timeout, in seconds, to wait for server to respond for health checks. This value should be increases for slow/unstable networks.

## Section [mail]

### enabled
**Default value:** `false`

Enable / disable email alerts from agent.

### smtp_from
**Default value:** none

Sender email address for alerts.

### smtp_to
**Default value:** none

Alerting recipients - a space separated list of email addresses.

### smtp_host
**Default value:** none

SMTP hostname.

### smtp_port
**Default value:** none

SMTP port number.

### smtp_user
**Default value:** none

SMTP username.

### smtp_password
**Default value:** none

SMTP password.

### smtp_mode
**Default value:** `tls`

SMTP connection mode - `plain`, `tls`, `starttls`. 

## Section [modules]

Module section configures what modules agent should load and report from.

For built in modules, the entries are key-value format, with key being the built in module name,
and value being true or false, indicating whether or not this module should be enabled.

For external modules, the entries are key-value format, with key being the module name and
value being path to the module executable.

External modules may not be prefixed with prefix `mod_` - this prefix is reserved for
built in modules.

### mod_facter
**Default value:** `true`

### mod_fs
**Default value:** `true`

### mod_lwall
**Default value:** `false`

### mod_res
**Default value:** `true`

### mod_systemd
**Default value:** `true`

### mod_apt
**Default value:** `false`

### mod_osquery
**Default value:** `false`
