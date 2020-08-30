---
title: mod_lwall
sidebar_label: mod_lwall
---

## About

This module audits and reports network port policy and configuration. It is designed to audit that:

- Network ports are bound to the expected interfaces.
- There are no rogue ports not compliant to the policy.

## System requirements

None.

## Alerts

CRITICAL level alert will be emitted when network policy is violated.

## Metadata

- List of policy violations, if any.
- List of ports and interfaces they are bound to.

## Metrics

None

## Configuration

### Section [mod_lwall]

#### policy_any
**Default value:** `restrict`

Default policy for all-interfaces bound INET ports. Set to `allow` to permit rogue ports to bind to system wide interfaces -
`0.0.0.0` for IPv4, `::` for IPv6.

#### policy_loopback
**Default value:** `restrict`

Default policy for loopback bound INET ports. Set to `allow` to permit rogue ports to bind to loopback interfaces -
`127.0.0.1` for IPv4, `::1` for IPv6, and `::ffff:127.0.0.1` for IPv4/6.

#### policy_bound
**Default value:** `restrict`

Default policy for interface bound INET ports. Set to `allow` to permit rogue ports to bind to specific interfaces.

### Section [mod_lwall_map]

This section contains a list of per-port policies, as key value pairs where the INET port is key, and policy rules is value.

Each port can have one or more policy entries, separated by a space. Possible policy rules are:

- `loopback` - permit loopback interface (`127.0.0.1`, `::1`, and `::ffff:127.0.0.1`).
- `any` - permit any interface (`0.0.0.0`, `::`).
- interface address - for specific interfaces.

## Example configuration

```ini
[mod_lwall]
policy_any = restrict
policy_loopback = restrict
policy_bound = restrict

[mod_lwall_map]
80 = any
443 = any
1234 = loopback 10.10.10.32 10.10.10.33
2345 = loopback
```
