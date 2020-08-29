---
title: Network setup
sidebar_label: Network
---

Gullveig platform, by default, uses two public ports - `8765` for reporting server, and `8770` for web user 
interface.

Port `8765` should be accessible to any hosts or networks you intend to install monitoring and reporting agents on.
Agents will fail to connect and report failure if this port is not accessible.

Port `8770` should be accessible to any hosts or networks you intend to access web user interface from.

By default, all Gulveig services will bind to `127.0.0.1` exclusively to prevent accidentally exposing networked
services to the public internet. You should change this value to the interface you want Gullveig 
services to bind to, unless having a single node setup is your goal - in that case, you should use
`127.0.0.1` for the reporting server process, and bind web user interface to listen on whatever interface
you want it to be accessible from.

Currently, it is not possible to bind Gullveig processes to more than one interface. If for any reason you require
such a configuration, you can either bind to all interfaces, or seek for alternative solutions.

