# Collection + Storage Strategy (Summary)

## Exporters (where they run)
- GPUs: `dcgm-exporter` on every GPU host
- Hosts: `node_exporter` on every host
- BMC: `ipmi_exporter` (multi-target) per cell/row; optional Redfish exporter where needed
- PDUs/UPS/Switches: `snmp_exporter` (multi-target) per row/zone
- Cooling: translator exporter on facilities gateways (Modbus/BACnet/SNMP/REST → Prometheus)

## Sharding (“cells”)
Define a **cell** as ~200 GPU servers and run **2 Prometheus scrapers per cell** (HA).
Each cell scraper scrapes:
- node_exporter + dcgm-exporter on its host set
- ipmi_exporter (multi-target) for the BMC IPs of those hosts
- row/zone snmp_exporter and facilities gateway endpoints (or separate “row Prom” if you prefer)

## Global store
Prometheus remote_write → Grafana Mimir (global). Mimir stores TSDB blocks in object storage.

## Retention tiers (suggested)
- Raw (15s/30s): 7–14 days
- 1m rollups: 30–90 days
- 5m/15m rollups: 6–18 months

## Cardinality controls
Allowed labels: dc, row, rack, cell, host, gpu (index)
Avoid: serial, uuid, mac, pid, container_id, pod_uid, job_id, free-text error strings
