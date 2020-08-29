---
title: mod_fs
sidebar_label: mod_fs
---

## About

This module reports and monitors host file systems.

This module neither reports nor monitors SquashFS file systems.

## System requirements

None.

## Alerts

INCIDENT level alert will be emitted when there is less than 10% free space remaining for any given mount point.

CRITICAL level alert will be emitted when there is less than 5% free space remaining for any given mount point.

## Metadata

Mount points, mount point options and device.

## Metrics

This module reports usage of each individual mount point on the host system.

## Configuration

### Section [mod_fs]

#### ignore_ro
**Default value:** `true`

Ignore read-only file systems, other than SquashFS.
