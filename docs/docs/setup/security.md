---
title: Security considerations
sidebar_label: Security
---

Gullveig is a networked system, and as such requires some consideration to be deployed securely. Gullveig can
also contain potentially sensitive information about the infrastructure it is monitoring. As such, it requires
some basic security considerations before being deployed.

## Networking security

All traffic between agents and reporting server is using mandatory TLS. It is not possible to disable or circumvent
this feature. The same principle applies to web server as well - all web assets, reports and API calls are
using HTTPS, and this too can be neither disabled, nor circumvented.

The agents, the reporting server, the web interface server - these components simply do not contain any code that 
could allow those components to accept non-TLS communications without modifying the software itself.

Despite the measures taken to make Gullveig web services secure, as with any other system exposed to web,
there is no way to completely eliminate the  possibility that some components used by Gullveig might have 
unknown vulnerabilities. To mitigate this risk, it is recommended to not expose Gullveig to public internet.

### Network ports and services

| Port   | Component       | Purpose                             | Do open to                |
|--------|-----------------|-------------------------------------|---------------------------|
| `8765` | gullveig-server | Incoming communications from agents | Hosts with known agents   |
| `8770` | gullveig-web    | Web user interface                  | User interface user hosts |

Gullveig reporting server exposes a single port it listens to for connections from agents. This port, by default, is 
`8765`. This port should only be made accessible to networks or IP addresses you need agents to be able to reach the
reporting server from. Reporting server port should never be open to public internet to prevent denial of service.

Gullveig web interface server exposes a single port, by default, `8770`. This port accepts HTTPS traffic
exclusively and should be made available to networks or IP addresses you intend to access the web interface from. Despite
the fact that the user interface requires strong authentication, is built to handle moderate amount of load one could expect
for such a service, the web interface server is not designed to handle public traffic. In theory, a malicious actor could
use this web service for denial of service against the host of the server.


## Data security

Only one Gullveig component currently persists any data to disk - reporting server. The persisted data includes
current and actual metadata reported by the agents, historic metrics, health status etc.

All data is located in a database that can be found, by default, in a directory `/var/lib/gullveig/`.
This database is NOT encrypted at rest. You should limit access to this database by means of limiting access to 
system users assigned to reporting server and web server only. There should be no need for any other system
users to access this directory, for any reason, with the sole exceptions being backing up the data and 
custom services designed to read the server database.

If you intend to send and store highly sensitive information about your services to the reporting server, consider
if you might want to encrypt the server data directory - either by setting up a full disk encryption or by 
using solutions such as eCryptfs, EncFS and similar. This should, however, not be required to store common
operating system metrics, health information etc.


## Logging and auditing access

All significant events are logged to `gullveig-web` and `gullveig-server` process output. These include,
every time agent connection is made, agent authorization fails or succeeds, user attempts to sign in or does sign in
to the web user interface.

Gullveig does not write logs to files. It is your responsibility to route logging output from stdout of the process
to the log aggregation system you prefer. Normally, this should be already handled by SystemD or any other supervisor,
or process management service.
