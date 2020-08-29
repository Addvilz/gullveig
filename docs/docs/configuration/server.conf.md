---
title: server.conf
sidebar_label: server.conf
---

Gullveig server configuration reference.

## Section [server]

### bind_to
**Default value:** `127.0.0.1`

Network interface to bind the reporting server to. This should most likely be changed during installation. Value defaults to loopback interface to prevent accidentally exposing the server to WAN. 

### bind_port
**Default value:** `8765`

Network port to expose the server for on. Only agents will use this port to connect to the server.

### ssl_certificate
**Default value:** none

Server TLS certificate.

### ssl_certificate_key
**Default value:** none

Server TLS key.

### client_key
**Default value:** none

Client key that agents will send to identify themselves with the reporting server. Should be a random string token with the minimum length of 128 bits.

### data_dir
**Default value:** `/var/lib/gullveig/`

Server data directory where server database will be located.

### service_timeout
**Default value:** `120`

Number of seconds to allow for service health status to not be reported. If exceeded, the server will change the service status to UNKNOWN and issue alerts.

## Section [mail]

### enabled
**Default value:** `false`

Enable / disable email alerts from agent.

### smtp_from
**Default value:** none

Sender email address for alerts.

### smtp_to
**Default value:** none

Alerting recipients - a space separated list of email addresses.

### smtp_host
**Default value:** none

SMTP hostname.

### smtp_port
**Default value:** none

SMTP port number.

### smtp_user
**Default value:** none

SMTP username.

### smtp_password
**Default value:** none

SMTP password.

### smtp_mode
**Default value:** `tls`

SMTP connection mode - `plain`, `tls`, `starttls`. 
