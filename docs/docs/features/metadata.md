---
title: Metadata
sidebar_label: Metadata
---

Gullveig allows remote agents to collect and report metadata - various facts and information about the host and services
the agent is monitoring.

Metadata is gathered by [modules](../modules/overview.md) and is viewable in Gullveig web user interface.

This feature allows for exploration and viewing of remote state of the host systems, such as
network interface configuration, host properties, software versions, and other useful information.

Agents report metadata periodically in the same way metrics and status is reported.

Metadata is reported as and visualized as rich tree-like data structure, and is designed to be able to report and
display almost any data structure possible - tables of data, lists, nested data, etc.
