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
- Gullveig web user interface is guaranteed compatible with the same reporting server version.

Simplifying, new servers support older agents within the same major version, but new agents are not guaranteed to be compatible with old servers. Web user interface version must match the reporting server version.

For example, server with version `0.1.5` is compatible with agents `0.1.5` or older. Agent with version `0.1.5` is compatible with servers up to, but excluding version `1.0.0`. Web user interface version `0.1.5` is only compatible with reporting server version `0.1.5`.
