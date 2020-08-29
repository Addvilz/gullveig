---
title: Agent setup
sidebar_label: Agent setup
---

**IMPORTANT:** before proceeding, ensure the reporting server is running and reachable from
the host you are installing the agent to.

## Create system user

Gullveig agents should be set up to use unprivileged user. Skip this step when deploying agent
to host with Gullveig reporting server.

```bash
useradd -r gullveig
```

## Create configuration directory

By default, all Gullveig agent configuration files should be located in directory `/etc/gullveig/`. This is a common 
configuration directory shared between agent, server and web user interface. Skip this step when deploying agent
to host with Gullveig reporting server.

```bash
mkdir -p /etc/gullveig/
```

## Create the agent data directory

Reporting agents require a directory to store agent metadata - connection settings, etc. By default, the data directory
is located at `/var/lib/gullveig/`. Skip this step when deploying agent to a host with Gullveig reporting server.

```bash
makdir -p /var/lib/gullveig/
```

## Create agent configuration file

Create a file `/etc/gullveig/agent.conf` and edit it with contents shown bellow. 
Modify the configuration options where required.

```ini
[agent]
# Ident - identifier of this reporting node. 
# By default - reverse FQDN of the host.
;ident = com.example.server1

# Data directory for Gullveig agent
;data_dir = /var/lib/gullveig/

# Number of workers to use to gather information. 
# By default - the number of CPU cores on the system / 2 
;mod_workers = 5

# Seconds to wait between sending reports
;report_delay = 5

# Seconds to wait between reattempting to reconnect to reporting server
;reconnect_delay = 10

# Assume server is down and alert after waiting ~120 seconds for reconnect
;server_ko_grace = 120

# Timeout to wait for server to respond for health checks. 
# Increase for slow/unstable networks.
;ping_timeout = 1

[mail]
# Alerting configuration - disabled by default.
# Used to send alerts when agent is not able to reach reporting server.

;enabled = false
;smtp_from = alerts@example.com
;smtp_to = recipient1@example.com recipient2@example.com
;smtp_host = smtp.example.com
;smtp_port = 587
;smtp_user = smtp_user@example.com
;smtp_password = example

# SMTP mode - plain, tls, starttls. By default - tls.
; smtp_mode = tls

[modules]
# Module configuration: [name] = [value]
# For internal mods: [name] = [true|false] to enable or disable module.
# For shell mods: [name] = [file_to_execute]

;mod_facter = true
;mod_fs = true
;mod_res = true
;mod_systemd = true
;mod_apt = false
;mod_osquery = false
;external_mod = /home/user/example-script.sh arg1 arg2 arg3

[mod_fs]
# Should we ignore read-only file systems? Default: true
;ignore_ro = true

[mod_osquery]
# osquery configuration file

; config = osquery.yml

[mod_systemd]
# Service name = expected status

; dnsmasq = inactive
; nftables = active
```

## Optional - create systemd service

1. Create a file `/etc/systemd/system/gullveig-agent.service`
2. Ensure the file is owned by root: `chown root:root /etc/systemd/system/gullveig-agent.service`
3. Ensure the file permissions are correct: `chmod 0644 /etc/systemd/system/gullveig-agent.service`
4. Edit the file with the contents bellow:

```ini
# systemd unit file for gullveig-agent

[Unit]
Description=Gullveig Agent

[Service]
ExecStart=gullveig-agent --conf /etc/gullveig/agent.conf
Environment=PYTHONUNBUFFERED=1
Restart=on-failure

User=gullveig
Group=gullveig

[Install]
WantedBy=default.target
```

Once you have completed the setup, execute `systemctl enable gullveig-agent` to enable the agent to start during system 
boot and execute `systemctl start gullveig-agent` to start the agent service.

## Ensure file-system permissions

| Path                                       | Owner    | Group    | Permissions |
|--------------------------------------------|----------|----------|-------------|
| /etc/gullveig/agent.conf                   | gullveig | gullveig | 0440        |
| /var/lib/gullveig/                         | gullveig | gullveig | 0740        |
| /etc/systemd/system/gullveig-agent.service | root     | root     | 0644        |
