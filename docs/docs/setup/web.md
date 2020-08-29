---
title: Web user interface setup
sidebar_label: Web setup
---

Gullveig platform provides an embedded web user interface that allows you to monitor service state, 
access agent reported metadata, view metric history and review service health history. 

Deploying the web user interface is recommended, but optional - web user interface is not strictly required if 
your goal is to receive service alerts from the reporting server.

Web user interface generally should be deployed on the same host as reporting server. This is because the interface 
api server effectively reads data from the reporting server database directly, without using any other facilities
to access the data.

For this stage assume you have already completed the [reporting server setup](./server.md).

## Generate web server certificate and key

Gullveig web user interface requires certificate and key to operate - all traffic to and from the web user interface
server is available exclusively over HTTPS.

To obtain a certificate for the web user interface, you can either:

1. Recommended - obtain the certificate from a certificate authority, e.g. LetsEncrypt.
2. Generate a self signed certificate, using the command bellow.

**IMPORTANT:** never reuse the reporting server certificate and key for web user interface server.

```bash
openssl req -nodes -x509 -newkey rsa:4096 \
  -keyout /etc/gullveig/web_cert.pem \
  -out /etc/gullveig/web_key.pem \ 
  -days 3650
```

## Generate web server secret

Web server secret token is used to sign user authentication tokens whenever user authenticates by using the web 
user interface. It is important to keep this secret private and random. Access to this secret will allow
anyone with access to the user interface to sign in and impersonate any user.

You can generate the secret using this command.

```bash
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1
```

## Create web user interface configuration file

Create a file `/etc/gullveig/web.conf` and edit it with contents shown bellow. 
Modify the configuration options where required.

```ini
[web]
# Interface and port for the web server to bind to.
# Uncomment and replace 127.0.0.1 to 0.0.0.0 to listen on all interfaces.

;bind_to = 127.0.0.1
;bind_port = 8770

# SSL certificate to use for the web UI server
ssl_certificate = web_cert.pem
ssl_certificate_key = web_key.pem

# Signing key for authentication tokens. CHANGE THIS.
secret = REPLACE ME WITH THE SERVER SECRET

[users]
# Web UI users and password.
# Use command `mkpasswd --method=SHA-512 --stdin` to hash a new user password.

# admin:admin
# admin = $6$tKs0/AQLUERKxY$L/YoYlvSvU0U4n6q8q6ZWnlfTdR6tK3feDwJJRHsGWd19sXOLdFxyILG2wvXMxcxd2RwoDmtvQCTNzlUTVsna1

[server]
# Point to the data directory of the reporting server
;data_dir = /var/lib/gullveig/
```

## Optional - create systemd service

1. Create a file `/etc/systemd/system/gullveig-web.service`
2. Ensure the file is owned by root: `chown root:root /etc/systemd/system/gullveig-web.service`
3. Ensure the file permissions are correct: `chmod 0644 /etc/systemd/system/gullveig-web.service`
4. Edit the file with the contents bellow:

```ini
# systemd unit file for gullveig-web

[Unit]
Description=Gullveig Web User Interface

[Service]
ExecStart=gullveig-web --conf /etc/gullveig/web.conf
Environment=PYTHONUNBUFFERED=1
Restart=on-failure

User=gullveig
Group=gullveig

[Install]
WantedBy=default.target
```

Once you have completed the setup, execute `systemctl enable gullveig-web` to enable web user interface to 
start during system boot and execute `systemctl start gullveig-web` to start the web user interface service.

## Ensure file-system permissions

| Path                                     | Owner    | Group    | Permissions |
|------------------------------------------|----------|----------|-------------|
| /etc/gullveig/web.conf                   | gullveig | gullveig | 0440        |
| /etc/gullveig/web_cert.pem               | gullveig | gullveig | 0440        |
| /etc/gullveig/web_key.pem                | gullveig | gullveig | 0440        |
| /etc/systemd/system/gullveig-web.service | root     | root     | 0644        |

