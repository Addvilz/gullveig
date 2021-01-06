---
title: Upgrading Gullveig
sidebar_label: Upgrading
---

## Upgrading components 

To upgrade Gullveig reporting from one version to another, follow these steps. It is important to follow the upgrade guide as shown - failure to do so can result in data loss.

**IMPORTANT**: Always upgrade reporting server first, then web, then agents.

### 1. Upgrade reporting server and web user interface

1. Upgrade `gullveig` package - `pip3 install --upgrade gullveig`
2. Stop `gullveig-web` process.
3. Restart `gullveig-server` process.
4. Wait for reporting server process to start.
4. Start `gullveig-web` process. 

### 2. Upgrade agents

1. Upgrade `gullveig` package - `pip3 install --upgrade gullveig`
2. Restart `gullveig-agent` process.

## Compatibility

- Agents are guaranteed compatible with reporting servers equal or newer than the agent version, within the same major version.
- Reporting server is guaranteed compatible with agents equal or older than the server version, within the same major version.
- Gullveig web user interface is guaranteed to be compatible with the same reporting server version.

Simplifying, new servers support older agents within the same major version, but new agents are not guaranteed to be compatible with old servers. Web user interface version must match the reporting server version.

For example, server with version `1.1.5` is compatible with agents `1.1.5` or older. Agent with version `1.1.5` is guaranteed compatible with servers up to, but excluding version `2.0.0`. Web user interface version `1.1.5` is only guaranteed compatible with reporting server version `1.1.5`.

As a general rule, backwards incompatible changes will be kept to the absolute minimum. Fundamental changes to the platform will always result in a major release.

### Compatibility of 0.x branch

Although initially planned for 0.x to be the first de-facto stable release, after months of testing it has become evident 0.x branch is not stable enough to be declared production release and is therefore except from backwards compatibility guarantee, retroactively.

This step has been taken to ensure the viability of the platform long-term. The first production-stable version of the platform will be 1.x, once released.
