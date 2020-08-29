---
title: mod_osquery
sidebar_label: mod_osquery
---

## About

This module provides integration with [osquery](https://osquery.io) and can emit metrics, health reports
and metadata based on pre-configured osquery queries.

## System requirements

- `osquery` must be installed.
- Python `osquery` [module](https://pypi.org/project/osquery/) must be installed - `pip3 install osquery`
- Gullveig agent user must be able to spawn osquery client sockets and query the database.

## Configuration

### Section [mod_osquery]

#### config
**Default value:** `osquery.yml`

File that contains query configuration for osquery.

## Configuring queries

Query configuration for osquery is stored in a separate YAML file, by default `/etc/gullveig/osquery.yml`.

This YAML file should contain up to 3 sections - `meta` for metadata queries, `metrics` for metric queries and `status` for status queries.

### Configuring metadata queries

Metadata queries can be of any format and return any value. All records returned from these queries will be stored as part of report and sent to the reporting server.

### Configuring metric queries.

Metric queries allow you to expose osquery data to Gullveig as regular metrics. 

Each query MUST return one or more records with following fields:

- `subject` - metric subject.
- `metric` - name of the metric counted.
- `from` - minimum value of this metric. `0` if there is no minimum.
- `to` - maximum value of this metric. `-1` if there is no maximum.
- `format` - metric format - `%` for percentage, `b` for bytes, or any other readable value.
- `value` - metric value.

Queries for metrics are constructed this way to allow for multiple metrics to be returned using a single query using aggregation.

### Configuring status metrics.

Status metrics allow to report service status based on osquery queries.

Each query must return exactly one record, and at least one field - `value` - a numeric resource status value - remaining space for a resource, etc. `value` can also be an indicator field, e.g. to indicate state of something.

Besides a query, each status query entry has following configuration fields:

- `subject` - subject of the status.
- `type` - status type - a freeform text.
- `is_metric` - boolean true, or false, if there is a matching metric with same subject and where type matches metric name in `metric` field.
- `threshold` - service threshold to compare the `value` to. Has two thresholds - `warning` and `critical`.

## Example query configuration

This configuration example helps illustrate how to configure osquery queries.

Each section of the configuration contains one or more entries. Except for `meta`, entry keys are used to describe the entry, whereas in `meta` section, the key will be used as metadata entry key.

Entry keys should be readable and unique - this will help you manage the configuration better.

```yaml
meta:
  running_containers: 'SELECT hostname, cpu_type from system_info'
  kernel_modules: 'select name from kernel_modules'

metrics:
  num_processes:
    query: >
      SELECT
        "processes" as `subject`,
        "count" as `metric`,
        0 as `from`,
        -1 as `to`,
        '' as `format`,
        COUNT(*) AS `value`
      FROM processes

status:
  num_processes:
    subject: processes
    type: count
    is_metric: false
    threshold:
      warning: 200
      critical: 250
    query: >
      SELECT COUNT(*) AS `value` FROM processes
``` 
