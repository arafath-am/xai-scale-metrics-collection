# Network & Security (Collection)

## Segmented networks
1) Compute mgmt: host exporters (9100/9400)
2) BMC OOB: IPMI/Redfish endpoints
3) Infra mgmt: switches/PDUs/UPS via SNMP
4) Facilities/OT: cooling plant controllers
5) Observability services: Prom scrapers + remote_write egress

## Rules
- Prom scrapers reach host exporters and exporter gateways.
- ipmi_exporter reaches BMC OOB (IPMI/Redfish).
- snmp_exporter reaches SNMP devices.
- Facilities controllers are only reachable via gateways.

## Secrets
- Vault for BMC creds + SNMPv3 secrets + facility gateway creds
- Vault Agent templates render local config files; rotation via restart/reload
