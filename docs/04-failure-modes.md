# Failure Modes & Mitigations

## Exporter down (node/dcgm)
- Detect via `up == 0`
- Mitigate with systemd restart + health checks

## BMC unreachable
- Detect via ipmi_exporter scrape errors
- Mitigate with HA exporters; network ACL checks; timeout tuning

## SNMP timeouts
- Reduce walk size (modules), increase parallelism, add exporters

## remote_write backpressure
- Watch `prometheus_remote_storage_samples_pending`
- Tune remote_write queue/shards; scale Mimir ingest tier; reduce metric volume if necessary
