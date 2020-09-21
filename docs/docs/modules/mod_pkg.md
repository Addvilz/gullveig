---
title: mod_pkg
sidebar_label: mod_pkg
---

**Introduced in version:** 0.1.18

## About

This module monitors for package updates using supported package management tools. This module is 
designed to be able to monitor multiple sources of package information simultaneously, including system
and userspace package managers.

### Package manager support 

Supported package management systems / tools:

- APT
- DNF

Future support planned for (in order of priority):

- YUM
- PIP
- NPM
- Gradle
- Maven
- Composer

## System requirements

### APT support

For systems using APT package manager (Debian, Ubuntu, etc) - `python3-apt` package must be installed

APT cache must be automatically updated by the system itself - Gullveig has no root access
and can't update APT cache on its own.

### DNF support 

For systems using DNF - `dnf` Python3 module must be present, provided by `python3-libdnf`.

**NOTE ON EL7:** this module does not support DNF on EL7 because EL7 based distributions does not provide
`python3-libdnf` bindings. On EL7, YUM will be used instead.

## Alerts

This module will issue an INCIDENT level alerts when updates are available, if `upgrade_warn` is set to `true`.

## Metadata

This module will report all pending updates in metadata of this module.

## Metrics

None.

## Configuration

### Section [module_reporting]

#### mod_pkg_fetch_every
**Default value:** `600` seconds

#### mod_pkg_expires_after
**Default value:** `660` seconds

### Section [mod_pkg]

#### upgrade_warn
**Default value:** `false`

When enabled, module will issue INCIDENT level alert when updates are available. Disabled by default.
