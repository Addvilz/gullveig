---
title: Configuring Gullveig
sidebar_label: Configuration
---

Gullveig uses plain text INI file format for configuration.

Comments and guidelines are prefixed using hash (`#`).

Default configuration keys and values are prefixed using semicolon (`;`). 

Both semicolon and hash are parsed as comment characters - the distinction is a semantic and there is no functional
difference between using either one of the comment characters. They are simply used to make the configuration files
more readable.


## Compartmentalizing complex configuration

Gullveig will automatically look for `.d` directory related to any service configuration files.

For example, given a configuration file `/etc/gullveig/agent.conf`, Gullveig will also look for a directory
`/etc/gullveig/agent.conf.d` - all `.conf` files in this directory will be loaded and their values will replace the 
ones initially defined in `/etc/gullveig/agent.conf`.
 
When a `.d` directory is encountered, all `.conf` files from that directory will be loaded, and their contents
will take precedence over the base configuration file the directory is related to.
 
This feature is useful for two things - to keep the main configuration files from becoming too crowded, and to 
install local overrides for global defaults.


The files in `.d` directory will be loaded by priority, for example, `5-local.conf` would be loaded before `10-local.conf`.
Configuration files without any priority prefix will be loaded in arbitrary order.
