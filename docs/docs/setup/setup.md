---
title: Setting up Gullveig
sidebar_label: Getting started
---

## Introduction

Gullveig platform consists of three main components:

- Server - aggregates, records and stores information reported by agents.
- Agents - reads, processes and transmits the host, service and other information to Server.
- Web - server that hosts web user interface and provides facilities to read from Server database.

To deploy Gullveig, you will need to designate a host to run Gullveig Server and Gullveig Web. Both Server and Web
must be deployed on the same host. 

Deploying Web is not mandatory, but recommended as it provides useful and convenient status and insights dashboards
for you to be able to check actual status of all monitored services in one place.

Gullveig Server and Web host requirements depend on the number of agents and amount of data that needs processing. 
A virtual machine with 256MB of RAM and single CPU core is more than enough to host Server and Web 
for about 10 to 20 agents reporting basic metrics, metadata and status every 2-5 seconds. Server and Web benefits
greatly to have the built in database server from fast storage - using SSD or NVME drives for this purpose
is recommended.

Gullveig Agent requirements depend entirely on the number of checks, metadata retrievals and metric reads performed
within the reporting interval, however, the agent process is generally light-weight enough to not be noticeable on
anything, but the most resource constrained environments.

Agents can be configured to reduce parallelism of how many modules can gather information at any given time, further
reducing peak resource use of each agent - by default, Agents will limit themselves to run no more than `cpu_cores / 2`
modules in parallel - see [agent.conf](../configuration/agent.conf.md) for how to configure agents.

## Deployment checklist

- Review [security considerations](./security.md)
- Review [network setup](./network.md)
- Review [system requirements](./requirements.md)
- [Install Gullveig](./installation.md)
- Deploy basic [reporting server](./server.md)
- Deploy basic [web ui](./web.md)
- Deploy one or more [agents](./agent.md)

## Configuration and defaults

Gullveig ships with sane, basic, zero-dependency default configuration examples. It is a good starting point
to deploy Gullveig services using the provided defaults and modify them as needed later.

There are several configuration parameters you might need to set that have no defaults, such as
users, passwords, agent keys. Such options will be clearly marked in the documentation
of each deployment stage.
