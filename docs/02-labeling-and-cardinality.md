# Labeling & Cardinality Controls

Large fleets usually fail from **label chaos**.

## Required labels (stable)
- `dc`, `row`, `rack`
- `cell`
- `host` (or `instance`)
- `gpu` (0..7) for per-GPU metrics

## Ban / avoid fleet-wide
- `serial`, `uuid`, `mac`, `pci_bus_id`
- `pid`, `process`, `container_id`, `pod_uid`, `job_id`
- any free-text label containing error strings

## Practical controls
- Exporter allowlists (dcgm-exporter metric selection)
- Prometheus relabeling to drop labels/metrics
- Recording rules to publish low-cardinality rollups (per rack/cell)
