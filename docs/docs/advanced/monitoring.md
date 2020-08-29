---
title: Advanced monitoring
sidebar_label: Monitoring
---

## Distributed monitoring

For remote service monitoring and to ensure high value service availability, you can architect your monitoring and use more than one agent to monitor the same remote service from multiple hosts.

This is very useful in monitoring reachability of remote APIs, networked services and such. As a simple example, besides monitoring their own hosts, you could reuse several agents to monitor reachability of remote resources.  

## Monitoring remote services without local agents

In some cases, remote agents cannot be deployed to monitor host-local resources - for example, remote APIs, serverless resources, network devices, etc.

To monitor such remote resources you can use "virtual agents". A host (server, virtual machine, etc.) can have more than one agent process running in parallel, and each of the agents can have completely independent configuration - you can instruct `gullveig-agent` to use a different configuration file using `--config` command line flag.

The recommended way to monitor remote resources where agent cannot be deployed is to deploy one or more "virtual" agents on a host machine with access to the remote resources - you can either deploy a dedicated host for remote monitoring or resources permitting - reuse the host running the reporting server.

Each virtual agent should then be configured with [ident](../configuration/agent.conf.md#ident) appropriate to the remote service (or service group) being monitored, and have only the modules that you need to monitor the remote resources enabled. All default modules should be disabled to not duplicate reporting about the host with virtual agents.
