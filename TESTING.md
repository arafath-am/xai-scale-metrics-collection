# Local Testing Guide

This guide explains how to run and test the xAI-scale monitoring stack locally using Docker Compose.

## Quick Start

**Prerequisites:**
- Docker and Docker Compose installed
- 4GB RAM available
- Ports 3000, 8000, 9090, 9400 available

**Start the stack:**

```bash
docker-compose up -d
```

**Access the interfaces:**

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| Cooling Exporter | http://localhost:8000/metrics | - |
| Mock DCGM Exporter | http://localhost:9400/metrics | - |

**Stop the stack:**

```bash
docker-compose down
```

**Clean up volumes:**

```bash
docker-compose down -v
```

## What's Running

### Mock DCGM Exporter (Port 9400)
Simulates 8 NVIDIA H100 GPUs with realistic metrics:
- GPU temperature (40-85°C)
- Power usage (250-400W)
- Utilization (0-100%)
- Memory usage (60-78GB used out of 80GB)
- Clock speeds, PCIe throughput

**Test it:**
```bash
curl http://localhost:9400/metrics | grep dcgm_gpu_temp
```

### Cooling Exporter (Port 8000)
Production-grade exporter reading from `sample_payload.json`:
- Supply/return air temperatures
- Fan speeds
- Alarm states

**Test it:**
```bash
# Metrics endpoint
curl http://localhost:8000/metrics | grep cooling_

# Health check
curl http://localhost:8000/healthz
```

### Prometheus (Port 9090)
Scrapes both exporters every 10-30 seconds.

**Test queries:**
1. Open http://localhost:9090
2. Try these PromQL queries:

```promql
# Average GPU temperature
avg(dcgm_gpu_temp)

# Total power consumption
sum(dcgm_power_usage)

# GPU utilization over time
dcgm_gpu_utilization

# Cooling system status
cooling_supply_air_temp_celsius
```

### Grafana (Port 3000)
Pre-configured with Prometheus datasource and GPU dashboard.

**View the dashboard:**
1. Login: admin / admin
2. Navigate to Dashboards → "xAI-Scale GPU Datacenter Overview"
3. You'll see:
   - GPU temperatures (8 lines, one per GPU)
   - GPU utilization graphs
   - Power consumption
   - Memory usage
   - Cooling plant metrics
   - Summary stats (total power, avg temp, etc.)

## Testing Scenarios

### Scenario 1: Verify Metrics Collection

```bash
# Check Prometheus targets are up
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Expected output:
# {"job":"dcgm","health":"up"}
# {"job":"cooling","health":"up"}
# {"job":"prometheus","health":"up"}
```

### Scenario 2: Query GPU Metrics

```bash
# Get current GPU temperatures
curl -s 'http://localhost:9090/api/v1/query?query=dcgm_gpu_temp' | jq '.data.result[] | {gpu: .metric.gpu, temp: .value[1]}'

# Get GPUs over 70°C
curl -s 'http://localhost:9090/api/v1/query?query=dcgm_gpu_temp>70' | jq '.data.result[] | .metric.gpu'
```

### Scenario 3: Test Exporter Health

```bash
# Cooling exporter health
curl http://localhost:8000/healthz

# Should return:
# {"healthy": true, "staleness_seconds": <low number>, ...}

# Mock DCGM health
curl http://localhost:9400/health
```

### Scenario 4: Simulate Production Queries

Open Prometheus UI (http://localhost:9090/graph) and run:

```promql
# Cell-wide average temperature (production use case)
avg by (cell) (dcgm_gpu_temp)

# Power usage by host (production use case)
sum by (host) (dcgm_power_usage)

# Thermal throttling detection (production alert)
dcgm_gpu_temp > 82

# Cooling alarm count (production alert)
sum(cooling_unit_alarm)
```

## Troubleshooting

### Containers won't start

```bash
# Check logs
docker-compose logs

# Restart individual service
docker-compose restart prometheus
```

### No metrics in Prometheus

```bash
# Check Prometheus targets
docker-compose exec prometheus wget -qO- http://localhost:9090/api/v1/targets

# Check exporter is responding
curl http://localhost:9400/metrics
curl http://localhost:8000/metrics
```

### Grafana dashboard is empty

```bash
# Verify Prometheus datasource
docker-compose exec grafana wget -qO- http://prometheus:9090/api/v1/query?query=up

# Manually add dashboard:
# 1. Go to http://localhost:3000
# 2. Import dashboard from demo/grafana-dashboard.json
```

### Port conflicts

```bash
# Check what's using the ports
netstat -an | grep -E ':(3000|8000|9090|9400)'

# Change ports in docker-compose.yml if needed
```

## Extending the Demo

### Add more mock GPUs

Edit `mock_exporters/dcgm_exporter.py`:

```python
NUM_GPUS = 16  # Change from 8 to 16
```

Rebuild:
```bash
docker-compose up -d --build mock-dcgm
```

### Add custom recording rules

Create `demo/recording-rules.yml`:

```yaml
groups:
  - name: gpu_aggregations
    interval: 30s
    rules:
      - record: cell:gpu_temp:avg
        expr: avg by (cell) (dcgm_gpu_temp)
      
      - record: cell:gpu_power:sum
        expr: sum by (cell) (dcgm_power_usage)
```

Add to Prometheus config and restart.

### Test with real DCGM

If you have NVIDIA GPUs available:

```bash
# Install DCGM exporter on the host
# Then update docker-compose.yml to use host network for dcgm job
```

## Performance Notes

**Resource usage (typical):**
- Mock DCGM: ~20MB RAM
- Cooling Exporter: ~30MB RAM
- Prometheus: ~200MB RAM
- Grafana: ~100MB RAM

**Total: ~350MB RAM, <5% CPU on modern hardware**

The stack is intentionally lightweight to run on laptops during demos.

## Next Steps

After testing locally:

1. **Scale testing**: Modify `NUM_GPUS` to simulate larger deployments
2. **Add alerts**: Create alerting rules in Prometheus
3. **Test HA**: Run multiple Prometheus instances (cell architecture)
4. **Integrate Mimir**: Add Grafana Mimir as remote write target (requires separate deployment)
5. **K8s deployment**: Use manifests in `exporters/cooling_rest_exporter/k8s-deployment.yaml`

## Clean Up

Remove everything (containers, volumes, networks):

```bash
docker-compose down -v
docker network prune
```
