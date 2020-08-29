---
title: Server setup
sidebar_label: Server setup
---

## Create system user

Gullveig server should be set up to use unprivileged user.

```bash
useradd -r gullveig
```

## Create configuration directory

By default, all Gullveig server configuration files should be located in directory `/etc/gullveig/`. This is a common 
configuration directory shared between agent, server and web user interface.

```bash
mkdir -p /etc/gullveig/
```

## Create the server data directory

Reporting server requires a directory to store local database. By default, the data directory is
located at `/var/lib/gullveig/`.

```bash
makdir -p /var/lib/gullveig/
```

## Generate reporting server certificate and key

Gullveig reporting server requires a server certificate and key to secure communications between the agents
and reporting server. Once set up, agents will also use this certificate to verify identity of the reporting
server.

It is not required for the certificate to be issued by certificate authority - in our specific use case a self signed
certificate is perfectly acceptable option.

- Reporting server certificates are not bound to domain names - you can use any domain you like.
- Reporting server certificates can be self signed.
- It is perfectly fine to use certificates with extremely long expiration dates.

You can generate a basic server certificate and key using the command bellow. This command will generate a self-signed 
certificate and key with expiration period of ~10 years.

```bash
openssl req -nodes -x509 -newkey rsa:4096 \
  -keyout /etc/gullveig/server_key.pem \
  -out /etc/gullveig/server_cert.pem \ 
  -days 3650
```

Updating the certificate will require you to generate a new certificate and key, and have all agents paired to the 
server again. This process can be automated to ensure minimal service disruption.

## Generate the client key

Client key is a token string used for the reporting server to authenticate agents. All agents use the same 
client key. Client key can be a string of arbitrary length and should be random.

Client key should be kept secret. Knowing a client allows anyone to send arbitrary data to the reporting server,
impersonate agents, etc.

You can generate a reasonably good client key using this command.

```bash
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1
```

## Create server configuration file

Create a file `/etc/gullveig/server.conf` and edit it with contents shown bellow. 
Modify the configuration options where required.

```ini
[server]
# Interface and port for the server to bind to.
# Uncomment and replace 127.0.0.1 to 0.0.0.0 to listen on all interfaces.

;bind_to = 127.0.0.1
;bind_port = 8765

# SSL certificate and key to use for the server
ssl_certificate = server_cert.pem
ssl_certificate_key = server_key.pem

# Client key to use for the connecting agents
client_key = REPLACE ME WITH THE CLIENT KEY

# Server data directory
;data_dir = /var/lib/gullveig/

# Timeout after which all services will be marked down if no
# updates are received. Default: 120 seconds

;service_timeout = 120

[mail]
# Email alerts. Disabled by default. You should enable this.

;enabled = false
;smtp_from = alerts@example.com
;smtp_to = recipient1@example.com recipient2@example.com
;smtp_host = smtp.example.com
;smtp_port = 587
;smtp_user = smtp_user@example.com
;smtp_password = example

# SMTP mode - plain, tls, starttls. By default - tls.
; smtp_mode = tls
```

## Optional - create systemd service

1. Create a file `/etc/systemd/system/gullveig-server.service`
2. Ensure the file is owned by root: `chown root:root /etc/systemd/system/gullveig-server.service`
3. Ensure the file permissions are correct: `chmod 0644 /etc/systemd/system/gullveig-server.service`
4. Edit the file with the contents bellow:

```ini
# systemd unit file for gullveig-server

[Unit]
Description=Gullveig Server

[Service]
ExecStart=gullveig-server --conf /etc/gullveig/server.conf
Environment=PYTHONUNBUFFERED=1
Restart=on-failure

User=gullveig
Group=gullveig

[Install]
WantedBy=default.target
```

Once you have completed the setup, execute `systemctl enable gullveig-server` to enable reporting server to 
start during system boot and execute `systemctl start gullveig-server` to start the reporting server service.

## Ensure file-system permissions

| Path                                        | Owner    | Group    | Permissions |
|---------------------------------------------|----------|----------|-------------|
| /etc/gullveig/                              | gullveig | gullveig | 0550        |
| /etc/gullveig/server.conf                   | gullveig | gullveig | 0440        |
| /etc/gullveig/server_cert.pem               | gullveig | gullveig | 0440        |
| /etc/gullveig/server_key.pem                | gullveig | gullveig | 0440        |
| /var/lib/gullveig/                          | gullveig | gullveig | 0740        |
| /etc/systemd/system/gullveig-server.service | root     | root     | 0644        |

