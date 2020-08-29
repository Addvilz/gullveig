---
title: mod_res
sidebar_label: mod_res
---

## About

This module reports and monitors host system resources - CPU, memory and SWAP space (if any).

## System requirements

None.

## Alerts

INCIDENT level alert will be emitted when there is less than 30% free SWAP space remaining.

CRITICAL level alert will be emitted when there is less than 10% free SWAP space remaining.

INCIDENT level alert will be emitted when there is less than 10% free memory remaining.

CRITICAL level alert will be emitted when there is less than 5% free memory remaining.

INCIDENT level alert will be emitted when CPU use is between 90% and 95%.

CRITICAL level alert will be emitted when CPU use is above or equal to 95%.

## Metadata

None.

## Metrics

Actual CPU, SWAP and memory usage, as well as current CPU frequency.

## Configuration

None.
