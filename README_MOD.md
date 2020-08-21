# Extending Gullveig reporting

You can build your own reporting modules using any language or platform of your preference.

In essence, Gullveig agents can be configured to retrieve external reports from executables - scripts, binaries, anything really.

These external module executables are expected to produce JSON in stdout - a report. Agent will read this report and send it to reporting server for ingest.

Modules are per-agent - meaning you can have certain modules enabled only for certain agents, but not for others. That also implies that external modules need to be present on the host of each agent that is performing monitoring.

Some example modules you could make are:

- Module that calls custom REST service to retrieve reports on the same host.
- Module that calls remote REST service to report status.
- Anything really.

You can enable external modules in agent configuration, section `modules`, for example:

```ini
external_mod = /some/directory/example-module.py
```

Here is an example of external module monitoring SWAP usage.

```python
#!/usr/bin/python
import json

print(json.dumps({
    # Metadata: optional. Any JSON serializable content with any structure.
    'meta': {
        'hello': 'world'
    },
    # Metrics: optional. Array of metric objects.
    'metric': [
        {
            # Subject - what are we monitoring? SWAP.
            's': 'swap',
            # Metric - what are we counting? Bytes used.
            'm': 'used',
            # value - numeric value - how much of something? Bytes.
            'v': current_swap_bytes,
            # from - lowest possible value of `v` - 0 bytes (no swap).
            'f': 0,
            # to - maximum possible value of `v` (max swap). 
            't': max_swap_bytes,
            # Data format - b for bytes, % for percentage. You can use any unit here, will be shown in the UI as-is.
            'd': 'b'
        },
    ],
    # Status: optional. Array of status objects.
    'status': [
        {
            # Subject - what are we monitoring? SWAP.
            's': 'swap',
            # Type - what is the sub-unit we are monitoring? Bytes used.
            't': 'used',
            # Resource usage percentage, a number in range from 0.0 to 100.0. None/null if there is no countable resource for this status.
            'r': swap_used_percent,
            # Status - 0 = OK, 1 = WARNING, 2 = OUTAGE. Do NOT use any other values!
            'st': 2,
            # Related to metric? If `s` and `t` matches a metric with `s` and `m` keys.
            'm': True
        }
    ]
}
))
```

If you happen to be writing a module that could be used by wider community, consider writing it in Python and contributing it to Gullveig core modules.

The principle of work for internal modules is pretty much the same as external modules, except that they are shipped with Gullveig, are always implemented in Python, and are loaded as part of the agent process itself - not as external binary or script.

See source code for existing modules in `gullveig/agent/modules` for examples on how to implement internal modules.
