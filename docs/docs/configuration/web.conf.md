---
title: web.conf
sidebar_label: web.conf
---

Gullveig web user interface configuration reference.

## Section [web]

### bind_to
**Default value:** `127.0.0.1`

Network interface to bind the web server to. This should most likely be changed during installation. Value defaults to loopback interface to prevent accidentally exposing the server to WAN. 

### bind_port
**Default value:** `8770`

Network port to expose the server for on. Only agents will use this port to connect to the server.

### ssl_certificate
**Default value:** none

Web server TLS certificate. Make sure this certificate is different from the one used for reporting server.

### ssl_certificate_key
**Default value:** none

Web server TLS key. Make sure this certificate is different from the one used for reporting server.

### secret

**Default value:** none

Signing key for authentication tokens. Should be a random string token with the minimum length of 128 bits.

This value should be kept secret (no pun intended) and random. Knowing this value will allow for anyone to forge user credentials and allow access to the web interface.

## Section [server]

### data_dir
**Default value:** `/var/lib/gullveig/`

Server data directory to look for the server database.

## Section [users]

User section contains a list of users, as username password pairs, authorized to access the web interface.

Passwords are in shadow compatible format. Commands, such as `mkpasswd --method=SHA-512 --stdin` can be used to hash the user password.

Example:

```ini
[users]

# admin:admin
admin = $6$tKs0/AQLUERKxY$L/YoYlvSvU0U4n6q8q6ZWnlfTdR6tK3feDwJJRHsGWd19sXOLdFxyILG2wvXMxcxd2RwoDmtvQCTNzlUTVsna1
```
