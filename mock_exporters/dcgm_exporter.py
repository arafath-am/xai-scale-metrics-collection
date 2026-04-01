#!/usr/bin/env python3
"""
Mock DCGM exporter for local testing.

Generates fake GPU metrics that mimic NVIDIA's dcgm-exporter.
Useful for testing Prometheus scraping without real GPUs.
"""
import random
import time
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# GPU metrics (8 GPUs per host as typical in xAI-scale deployments)
NUM_GPUS = 8

gpu_temp = Gauge("dcgm_gpu_temp", "GPU temperature in Celsius", ["gpu", "uuid"])
gpu_power = Gauge("dcgm_power_usage", "GPU power usage in watts", ["gpu", "uuid"])
gpu_utilization = Gauge("dcgm_gpu_utilization", "GPU utilization percentage", ["gpu", "uuid"])
gpu_memory_used = Gauge("dcgm_fb_used", "GPU framebuffer used in MiB", ["gpu", "uuid"])
gpu_memory_free = Gauge("dcgm_fb_free", "GPU framebuffer free in MiB", ["gpu", "uuid"])
sm_clock = Gauge("dcgm_sm_clock", "SM clock frequency in MHz", ["gpu", "uuid"])
mem_clock = Gauge("dcgm_mem_clock", "Memory clock frequency in MHz", ["gpu", "uuid"])
pcie_rx = Gauge("dcgm_pcie_rx_bytes", "PCIe RX throughput bytes/sec", ["gpu", "uuid"])
pcie_tx = Gauge("dcgm_pcie_tx_bytes", "PCIe TX throughput bytes/sec", ["gpu", "uuid"])

# Generate fake but realistic GPU UUIDs
GPU_UUIDS = [f"GPU-{random.randint(10000000, 99999999):08x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}" for _ in range(NUM_GPUS)]

def update_metrics():
    """Generate realistic GPU metrics with some variation."""
    for i in range(NUM_GPUS):
        gpu_id = str(i)
        uuid = GPU_UUIDS[i]
        
        # Temperature: 40-85°C with some GPUs running hotter
        base_temp = 65 + (i * 2)  # GPUs later in the chain run slightly hotter
        temp = base_temp + random.uniform(-5, 10)
        gpu_temp.labels(gpu=gpu_id, uuid=uuid).set(min(85, max(40, temp)))
        
        # Power: 250-400W (typical for H100/A100)
        power = 320 + random.uniform(-50, 80)
        gpu_power.labels(gpu=gpu_id, uuid=uuid).set(power)
        
        # Utilization: Simulate training workload (high util with occasional drops)
        if random.random() < 0.9:  # 90% of time running hot
            util = random.uniform(85, 100)
        else:  # 10% of time idling (checkpointing, data loading)
            util = random.uniform(0, 30)
        gpu_utilization.labels(gpu=gpu_id, uuid=uuid).set(util)
        
        # Memory: 80GB total (H100), 60-78GB used during training
        total_mem = 81920  # MiB
        used_mem = random.uniform(61440, 79872)  # 75-97% utilization
        gpu_memory_used.labels(gpu=gpu_id, uuid=uuid).set(used_mem)
        gpu_memory_free.labels(gpu=gpu_id, uuid=uuid).set(total_mem - used_mem)
        
        # Clock speeds: SM at 1410-1980 MHz, Memory at 1593 MHz
        sm_clock.labels(gpu=gpu_id, uuid=uuid).set(random.uniform(1410, 1980))
        mem_clock.labels(gpu=gpu_id, uuid=uuid).set(1593)  # Fixed for HBM3
        
        # PCIe throughput: Simulate data pipeline
        pcie_rx.labels(gpu=gpu_id, uuid=uuid).set(random.uniform(1e9, 5e9))  # 1-5 GB/s
        pcie_tx.labels(gpu=gpu_id, uuid=uuid).set(random.uniform(1e8, 1e9))  # 100MB-1GB/s

@app.route("/metrics")
def metrics():
    update_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/health")
def health():
    return {"status": "healthy", "gpus": NUM_GPUS}

if __name__ == "__main__":
    print(f"Mock DCGM Exporter starting with {NUM_GPUS} GPUs")
    print("Metrics: http://0.0.0.0:9400/metrics")
    app.run(host="0.0.0.0", port=9400, threaded=True)
