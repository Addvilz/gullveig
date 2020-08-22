# Gullveig

![Gullveig](./gullveig.png)

## Distributed systems and service monitoring

Gullveig is a light-weight distributed system and service monitoring platform. Gullveig is trivial to deploy, portable and easy to maintain. Gullveig is written in Python and has no external dependencies.

1. Written in Python, no external dependencies.
2. Modular status monitoring system, using agents.
3. Service health monitoring, resource utilization and metric history.
4. Automated alerting via email.

## How does it work?

Gullveig consists of 3 main components - reporting server, agents and web UI. To deploy Gullveig, you will need to designate a reporting server host and setup a reporting server on it. Then, for each host you want to monitor, setup and configure an agent that will gather and report status to reporting server. You can view the overall status of your infrastructure using the web UI.

## Setup

NOTE: Gullveig is relatively new and is not yet well documented. Feel free to contribute.

Gullveig is fairly easy to setup - all you need is Python 3 installed on all the involved hosts. 
See [setup manual](./README_SETUP.md) for complete install guide.

Gullveig setup is designed to be easy to deploy both manually and using configuration management systems, such as Puppet or Ansible. Everything about the reporting agents, server and web can be configured automatically.

## Custom and embedded modules

Gullveig offers for monitoring using both embedded and external modules.

There are several embedded modules available:

- mod_facter - retrieves and reports host metadata using `facter`, if installed.
- mod_fs - monitors and reports file system state (mounts, utilization).
- mod_res - monitors and reports on host resource utilization (memory, cpu, swap).
- mod_systemd - monitors state of systemd services.
- mod_apt - lists available apt upgrades in meta, emits warning when upgrades are available (requires `python3-apt` to be installed independently)

You can create your own external modules using any programming language. See [how to create modules](./README_MOD.md).

By default, only `mod_facter`, `mod_fs`, `mod_res` and `mod_systemd` modules are enabled. You can enable other modules as needed
in the configuration file of each agent (`agent.conf`).

## License

Licensed under terms and conditions of Apache 2.0 license.
