---
title: mod_systemd
sidebar_label: mod_systemd
---

## About

This module monitors systemd service state.

## System requirements

- `systemctl` command must be present.

## Alerts

CRITICAL level alert when service status does not match the expected status.

## Metadata

None.

## Metrics

None.

## Configuration

### Section [mod_systemd]

A list of service and expected service statuses, as key value pairs.

Possible service statuses are - `active`, `inactive`.

Example:

```ini
[mod_systemd]

dnsmasq = active
nftables = active
```
