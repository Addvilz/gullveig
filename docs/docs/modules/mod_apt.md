---
title: mod_apt
sidebar_label: mod_apt
---

## About

This module monitors for pending system updates in APT based systems.

## System requirements

- Can only be used in APT based Linux distributions, such as Debian, Ubuntu, etc.
- `python3-apt` system package must be installed.
- APT cache must be automatically updated by the system itself because this operation would require root.


## Alerts

This module will issue an INCIDENT level alerts when updates are available.

## Metadata

This module will report all pending updates in metadata of this module.

## Metrics

None.

## Configuration

None.
