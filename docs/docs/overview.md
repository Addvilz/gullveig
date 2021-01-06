---
title: About Gullveig
sidebar_label: Overview
---

Gullveig is a free, open-source, light-weight infrastructure and service monitoring and operations support platform.
Gullveig offers monitoring, alerting, and insights services for servers, services and applications, as well
as other useful administrator and operations features.

Gullveig is modular and flexible, and allows for easy development of custom monitoring and reporting modules 
that can be created using nearly any platform or programming language.

## Core features

- Distributed and scalable agent based monitoring architecture.
- Modern, easy to use web interface.
- Time series graphs for resources, counters, metrics and performance data.
- Double-redundant bi-directional remote monitoring.
- Automated alerting and notifications about status changes.
- Rich interface for remote fact and metadata discovery.
- Interactive status dashboard.
- Simple, file based configuration.
- Wide operating system support (written in Python 3).
- Does not depend on third party software for basic operation.
- Built in static documentation server.

## Current status

Gullveig is actively developed and maintained, and is stable enough for production use, with caveats<sup>[1]</sup> - it is already used as primary
or as an additional monitoring tool in production deployments, sizes ranging from a handful to a few hundreds of nodes.

<sup>[1]</sup> Although stable enough for production use as a tool, the architecture of the platform itself is not final and is undergoing
extensive testing and development with production and high demand workloads. There are several major braking changes planned for 0.x version
line before 1.x will be released as production stable, mostly to deal with architecture optimization and performance, as well as number of 
new features.

All updates and new releases after and including 1.x are subject to the [compatibility policy](./setup/upgrading.md#compatibility).

[![Gullveig](/img/gullveig.png)](./webui.md)

## License

Gullveig is licensed under Apache 2.0 software license.

