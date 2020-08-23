# Installing Gullveig

Gullveig requires Python 3.5+. You can install Gullveig using PIP - `pip install gullveig`. Depending on your distribution, you might need to substitute `pip` with `pip3` to install Gullveig using Python 3 PIP.

The installation procedure is the same for all components of Gullveig - agent, server, and web UI.

**IMPORTANT:** all installation instructions are to be run as root user or using, for example, `sudo`.

## Requirements

- Python 3.5+, 
- PIP 3
- Python Setuptools
- Python development headers
- GCC

GCC and Python development headers are required to build binaries for reporting modules using native code and extensions, such as psutil.

On Debian based distributions, you can set up these dependencies using this command 

```
apt install python3 \
    python3-pip \ 
    python3-setuptools \
    python3-dev \
    gcc
```

## Securing your installation

Gullveig uses network servers (HTTP and websockets) to communicate between agents, and between web UI server and web visitors. All communications between agents and reporting server are using TLS that can not be disabled. Agents use pre-shared keys to authenticate to reporting server, and a kind of certificate pinning is used to verify reporting server authenticity. Gullveig web UI is also only available over TLS that can not be disabled.

As a general rule, you should never expose Gullveig services outside of your own network. Although both reporting server and web UI use strong authentication and TLS, that does not mean that either Gullveig itself or libraries used by Gullveig are not susceptible to some kind of abuse by third parties if exposed publicly.

The best possible way to deal with this issue is to firewall both reporting server port and web UI port so that they can only be accessed from hosts and networks you explicitly allow.

By default, Gullveig reporting server listens on port `8765` and web UI server listens on port `8770`.

You only need to expose port `8765` of reporting server to networks where agents are expected to connect from. Port `8770` needs to be accessible from wherever you intend to access the web UI from.

## Deploying reporting server

##### 1. Create a system user for server daemon

You can choose whatever username you prefer, as long as you use the same username for the entire process.

```shell script
useradd -r gullveig-server
```

##### 2. Create configuration directory

```shell script
mkdir -p /etc/gullveig/
```

##### 3. Generate server certificate and key

Gullveig reporting server requires TLS to be configured for it to be able to accept data from agents. Having a certificate is mandatory and there is no way to disable TLS for the server.

There are notable differences between Gullveig server certificates and certificates you might have setup previously for other services and systems.

1. Gullveig server certificates are not bound to a domain - you can use any domain.
2. Gullveig server certificates can be self signed.
3. Gullveig server certificates are fine to have long expiration times.

Gullveig certificate is used to pair agents and servers - for agents to verify server identity, and to encrypt all traffic between agents and server. During pairing process, you will be able to automatically retrieve the server certificate from the server.

You can generate a basic server certificate and key using the command bellow. This command will generate a self-signed certificate and key with expiration period of 10 years and 4096 bit RSA private key.

```shell script
cd /etc/gullveig/
openssl req -nodes -x509 -newkey rsa:4096 -keyout server_key.pem -out server_cert.pem -days 3650
```

**IMPORTANT:** make sure certificate and the private key is readable by `gullveig-server` user - it will fail to start otherwise. 

Updating the certificate in future will require you to generate a new certificate and key, and have all agents paired to the server again. This process can be automated to ensure minimal service disruption - see the section about how to pair agents and servers bellow.

##### 4. Create server configuration file

Create a file `/etc/gullveig/server.conf` and edit it with contents shown bellow. You can modify the options as needed.

```ini
[server]
# Interface and port of the server to bind to
# Change this to 0.0.0.0 to listen on all interfaces or specific IP of the interface to listen to.
bind_to = 127.0.0.1
bind_port = 8765

# SSL certificate to use for the server
ssl_certificate = server_cert.pem
ssl_certificate_key = server_key.pem

# Client key to use for the connecting agents
client_key = d8a928b2043db77e340b523547bf16cb4aa483f0645fe0a290ed1f20aab76257

# Server data directory
;data_dir = /var/lib/gullveig-server/

# Timeout after which all services will be marked down if no
# updates are received. Default: 120 second
;service_timeout = 120

[mail]
# Alerting configuration. Disabled by default.
enabled = false
smtp_from = alerts@example.com
smtp_to = recipient1@example.com recipient2@example.com
smtp_host = smtp.example.com
smtp_port = 587
smtp_user = smtp_user@example.com
smtp_password = example
# SMTP mode - plain, tls, starttls. By default - tls.
; smtp_mode = tls
```

##### 5. Create server data directory

```shell script
mkdir -p /var/lib/gullveig-server/
chown gullveig-server:gullveig-server /var/lib/gullveig-server/
chmod 0750 /var/lib/gullveig-server/
```

##### 6. Optional - create systemd service

1. Create systemd unit file at `/etc/systemd/system/gullveig-server.service`.
2. Change the file permissions `chmod 0644 /etc/systemd/system/gullveig-server.service`.
3. Edit the file with contents bellow:

```ini
# systemd unit file for gullveig-server

[Unit]
Description=Gullveig Server

[Service]
ExecStart=gullveig-server --conf /etc/gullveig/server.conf
Environment=PYTHONUNBUFFERED=1
Restart=on-failure

User=gullveig-server
Group=gullveig-server

[Install]
WantedBy=default.target
```

Finally, execute `systemctl enable gullveig-server` to enable server to start during boot time and `systemctl start gullveig-server` to start the server.

## Deploying web interface

Gullveig ships with embedded web UI for you to be able to monitor service state, access node metadata etc. Deploying the web UI is recommended, but optional - web UI is not needed to receive service alerts from the reporting server.

**IMPORTANT:** web UI *must be deployed on the same host as reporting server*. This is because web UI backend effectively reads
data from the reporting server database directly. Reporting server has no facilities to access the data. We should also reuse the same user and
group to run the web UI service.

##### 1. Generate web server certificate and key

Gullveig web UI server serves all content using HTTPS. Having a certificate is mandatory and there is no way to disable TLS for the web UI server.

To obtain a certificate for the web UI server you can either:

1. Recommended - obtain the certificate from a certificate authority, e.g. LetsEncrypt.
2. Generate a self signed certificate, using the same procedure as shown for the reporting server.

**IMPORTANT** - do not reuse the reporting server certificate for the web UI server.

##### 2. Create web server configuration file

Create a file `/etc/gullveig/web.conf` and edit it with contents shown bellow. You can modify the options as needed.

**IMPORTANT:** You MUST change the key `secret` in section `web`. This value is used to sign user interface authentication tokens. Using a random SHA256 hash value is okay. 

```ini
[web]
# Interface and port of the server to bind to
bind_to = 127.0.0.1
bind_port = 8770

# SSL certificate to use for the web UI server
ssl_certificate = web_cert.pem
ssl_certificate_key = web_key.pem

# Signing key for authentication tokens. CHANGE THIS.
secret = CHANGEME

[users]
# Web UI users and password. Use command mkpasswd --method=SHA-512 --stdin
# admin:admin
# admin = $6$tKs0/AQLUERKxY$L/YoYlvSvU0U4n6q8q6ZWnlfTdR6tK3feDwJJRHsGWd19sXOLdFxyILG2wvXMxcxd2RwoDmtvQCTNzlUTVsna1

[server]
# Point to the data directory of the reporting server
data_dir = /var/lib/gullveig-server/
```

##### 3. Optional - create systemd service

1. Create systemd unit file at `/etc/systemd/system/gullveig-web.service`.
2. Change the file permissions `chmod 0644 /etc/systemd/system/gullveig-web.service`.
3. Edit the file with contents bellow:

```ini
# systemd unit file for gullveig-web

[Unit]
Description=Gullveig Server

[Service]
ExecStart=gullveig-web --conf /etc/gullveig/web.conf
Environment=PYTHONUNBUFFERED=1
Restart=on-failure

User=gullveig-server
Group=gullveig-server

[Install]
WantedBy=default.target
```

Finally, execute `systemctl enable gullveig-web` to enable web UI to start during boot time and `systemctl start gullveig-web` to start the server.

## Deploying agents

**IMPORTANT:** before continuing, make sure your reporting server is running!

##### 1. Create a system user for agent daemon

```shell script
useradd -r gullveig-agent
```

##### 2. Create configuration directory

You can skip this step for hosts where this directory is already present.

```shell script
mkdir -p /etc/gullveig/
```

##### 4. Create agent configuration file

Create a file `/etc/gullveig/agent.conf` and edit it with contents shown bellow. You can modify the options as needed.

```ini
[agent]
# Ident - identifier of this reporting node. By default - reverse FQDN of the host.
; ident = com.example.server1
# Data directory for Gullveig agent
data_dir = /var/lib/gullveig-agent/

# Number of workers to use to gather information - default, number of CPU cores on the system 
;mod_workers = 5

# Seconds to wait after sending each report
report_delay = 5

# Seconds to wait between server connection attempts
reconnect_delay = 10

# Assume server is down and alert after ~60 seconds after disconnect
server_ko_grace = 60

# Timeout to wait for server to respond for health checks. Increase for slow/unstable networks.
ping_timeout=1

[mail]
# Alerting configuration - disabled by default.
# Used to send alerts when agent is not able to reach reporting server.
enabled = false
smtp_from = alerts@example.com
smtp_to = recipient1@example.com recipient2@example.com
smtp_host = smtp.example.com
smtp_port = 587
smtp_user = smtp_user@example.com
smtp_password = example

[modules]
# Module configuration: [name] = [value]
# For internal mods: [name] = [true|false] to enable or disable mod.
# For shell mods: [name] = [file_to_execute]
mod_facter = true
mod_fs = true
mod_res = true
mod_systemd = true
mod_apt = false
; external_mod = /home/user/example-script.sh arg1 arg2 arg3

[mod_systemd]
# mod_systemd service monitoring configuration - [service name] = [active|inactive]
;dnsmasq = active
;nginx = active
```

##### 5. Create agent data directory

```shell script
mkdir -p /var/lib/gullveig-agent/
chown gullveig-agent:gullveig-agent /var/lib/gullveig-agent/
chmod 0750 /var/lib/gullveig-agent/
```

##### 6. Pair agent and server

Execute the pairing command and follow instructions.

```shell script
gullveig-util pair --conf /etc/gullveig/agent.conf
```

After the pairing command, `gullveig-util` will create client configuration files in `/var/lib/gullveig-agent/`.
Files include `client.conf` to hold credentials and address of the server, and `server.pem` - a copy of the 
server certificate. This copy will be used to verify the identity of the reporting server.

##### 5. Optional - create systemd service

1. Create systemd unit file at `/etc/systemd/system/gullveig-agent.service`.
2. Change the file permissions `chmod 0644 /etc/systemd/system/gullveig-agent.service`.
3. Edit the file with contents bellow:

```ini
# systemd unit file for gullveig-agent

[Unit]
Description=Gullveig Agent

[Service]
ExecStart=gullveig-agent --conf /etc/gullveig/agent.conf
Environment=PYTHONUNBUFFERED=1
Restart=on-failure

User=gullveig-agent
Group=gullveig-agent

[Install]
WantedBy=default.target
```

Finally, execute `systemctl enable gullveig-agent` to enable agent start during boot time and `systemctl start gullveig-agent` to start the agent.

## Configuration files, compartmentalization and overrides

Whenever a configuration path is provided to any of the Gullveig CLI interfaces, Gullveig will automatically look for related ".d" directory. If exists, all `.conf` files from this directory will be loaded, and their contents will take precedence over the initially provided configuration file. This feature is useful for two things - to keep the main configuration files from becoming too crowded, and to install local overrides for global defaults.

The path of the ".d" directory is directly related to the configuration file path given - `agent.conf` will result in `agent.conf.d/`, `server.conf` will result in `server.conf.d` and so forth. 

For example, given a configuration file `/etc/gullveig/agent.conf`, Gullveig will also look for a directory `/etc/gullveig/agent.conf.d` - all `.conf` files in this directory will be loaded and their values will replace the ones initially defined in `/etc/gullveig/agent.conf`.

The files in ".d" directory will be loaded by priority, for example, `5-local.conf` would be loaded before `10-local.conf`. Configuration files without any priority prefix will be loaded in arbitrary order.
