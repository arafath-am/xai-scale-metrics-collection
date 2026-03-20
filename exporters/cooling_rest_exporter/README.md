# Cooling Plant Exporter - Deployment Guide

Prometheus exporter that translates cooling plant telemetry (from REST APIs, Modbus gateways, or BACnet controllers) into Prometheus metrics format.

## Configuration

Set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LISTEN_HOST` | `0.0.0.0` | Bind address |
| `LISTEN_PORT` | `8000` | HTTP port |
| `COOLING_API_URL` | _(empty)_ | REST API endpoint (if set, takes priority over file) |
| `COOLING_JSON_FILE` | `sample_payload.json` | Local JSON file path (fallback) |
| `POLL_INTERVAL` | `15` | Seconds between polls |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |

## Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with sample data
python app.py

# Run tests
pytest test_app.py -v
```

## Docker Deployment

```bash
# Build
docker build -t cooling-exporter:latest .

# Run
docker run -d \
  -p 8000:8000 \
  -e COOLING_API_URL=http://cooling-gateway/api \
  --name cooling-exporter \
  cooling-exporter:latest

# Or use docker-compose
docker-compose up -d
```

## Systemd Deployment

```bash
# Install
sudo mkdir -p /opt/cooling_exporter
sudo cp app.py sample_payload.json /opt/cooling_exporter/
python3 -m venv /opt/cooling_exporter/venv
/opt/cooling_exporter/venv/bin/pip install -r requirements.txt

# Configure service
sudo cp cooling-exporter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cooling-exporter

# Check status
sudo systemctl status cooling-exporter
sudo journalctl -u cooling-exporter -f
```

## Kubernetes Deployment

```bash
kubectl apply -f k8s-deployment.yaml

# Verify
kubectl -n monitoring get pods -l app=cooling-exporter
kubectl -n monitoring logs -l app=cooling-exporter
```

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: cooling
    scrape_interval: 30s
    static_configs:
      - targets: ['cooling-exporter:8000']
        labels:
          facility: datacenter-1
```

## Metrics Exposed

- `cooling_supply_air_temp_celsius{unit_id}` - Supply air temperature
- `cooling_return_air_temp_celsius{unit_id}` - Return air temperature
- `cooling_fan_speed_rpm{unit_id}` - Fan rotational speed
- `cooling_unit_alarm{unit_id}` - Alarm status (0=ok, 1=alarm)
- `cooling_fetch_total{status}` - Total fetch attempts (success/error)
- `cooling_fetch_errors_total{error_type}` - Fetch failures by type

## Health Check

```bash
curl http://localhost:8000/healthz

# Response:
{
  "healthy": true,
  "staleness_seconds": 12,
  "last_error": null,
  "threshold_seconds": 60
}
```

Status codes:
- `200` - Healthy (recent successful poll)
- `503` - Unhealthy (stale data, exceeds 4x poll interval)

## Troubleshooting

**No metrics appearing:**
- Check `/healthz` for staleness warnings
- Verify `COOLING_API_URL` is reachable
- Check logs for HTTP errors or JSON parse failures

**High memory usage:**
- Likely cardinality explosion from dynamic `unit_id` labels
- Review the number of unique cooling units being tracked

**Stale metrics:**
- Source API may be slow or timing out
- Increase `POLL_INTERVAL` if source is rate-limited
- Check network connectivity to cooling gateway
