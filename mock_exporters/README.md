# Mock Exporters

Simulated exporters for local testing without real hardware.

## DCGM Exporter

Generates realistic NVIDIA GPU metrics for 8x H100 GPUs:

- GPU temperature (40-85°C with variance)
- Power usage (250-400W)
- Utilization (0-100%, simulates training workload)
- Memory usage (60-78GB used out of 80GB HBM3)
- SM and memory clock speeds
- PCIe RX/TX throughput

**Run standalone:**

```bash
pip install -r requirements.txt
python dcgm_exporter.py
```

**Metrics endpoint:** http://localhost:9400/metrics

**Customize GPU count:**

Edit `dcgm_exporter.py` and change:
```python
NUM_GPUS = 8  # Change to 16, 32, etc.
```

## Why Mock Exporters?

Real DCGM requires:
- NVIDIA GPUs (H100/A100)
- CUDA drivers
- DCGM daemon

Mock exporters let you:
- Test Prometheus configs locally
- Demo the stack without hardware
- Develop dashboards and alerts
- Validate scrape performance

The metrics format matches real dcgm-exporter output, so configs are production-ready.
