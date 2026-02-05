#!/usr/bin/env python3
"""
Cooling plant metrics exporter for Prometheus.

Polls a REST API or reads JSON file, translates to Prometheus exposition format.
Designed for BACnet/Modbus gateways that expose cooling plant telemetry via HTTP.
"""
import json
import logging
import os
import signal
import sys
import threading
import time
from typing import Dict, Any, Optional

import requests
from flask import Flask, Response
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST

# Config from env
LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8000"))
COOLING_API_URL = os.environ.get("COOLING_API_URL", "")
COOLING_JSON_FILE = os.environ.get("COOLING_JSON_FILE", 
                                   os.path.join(os.path.dirname(__file__), "sample_payload.json"))
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "15"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)
log = logging.getLogger("cooling_exporter")

# Prom metrics
supply_temp = Gauge("cooling_supply_air_temp_celsius", 
                    "Supply air temperature in Celsius", ["unit_id"])
return_temp = Gauge("cooling_return_air_temp_celsius", 
                    "Return air temperature in Celsius", ["unit_id"])
fan_speed = Gauge("cooling_fan_speed_rpm", 
                  "Fan rotational speed in RPM", ["unit_id"])
unit_alarm = Gauge("cooling_unit_alarm", 
                   "Alarm status (0=ok, 1=alarm)", ["unit_id"])

fetch_total = Counter("cooling_fetch_total", "Total fetch attempts", ["status"])
fetch_errors = Counter("cooling_fetch_errors_total", "Fetch failures by type", ["error_type"])

app = Flask(__name__)
state = {
    "last_success_ts": 0,
    "last_error": None,
    "running": True
}

def fetch_data() -> Optional[Dict[str, Any]]:
    """Pull cooling plant data from REST API or fallback to file."""
    if COOLING_API_URL:
        try:
            resp = requests.get(COOLING_API_URL, timeout=5)
            resp.raise_for_status()
            fetch_total.labels(status="success").inc()
            return resp.json()
        except requests.RequestException as err:
            fetch_total.labels(status="error").inc()
            fetch_errors.labels(error_type=type(err).__name__).inc()
            log.error(f"HTTP fetch failed: {err}")
            raise
    
    # Fallback to local file
    try:
        with open(COOLING_JSON_FILE, "r") as f:
            data = json.load(f)
            fetch_total.labels(status="success").inc()
            return data
    except (OSError, json.JSONDecodeError) as err:
        fetch_total.labels(status="error").inc()
        fetch_errors.labels(error_type=type(err).__name__).inc()
        log.error(f"File read failed: {err}")
        raise

def update_gauges(data: Dict[str, Any]) -> None:
    """Parse JSON payload and update Prometheus gauges."""
    units = data.get("units", {})
    if not units:
        log.warning("No 'units' key in payload")
        return
    
    for unit_id, readings in units.items():
        try:
            if "supply_air_temp_c" in readings:
                supply_temp.labels(unit_id=unit_id).set(float(readings["supply_air_temp_c"]))
            if "return_air_temp_c" in readings:
                return_temp.labels(unit_id=unit_id).set(float(readings["return_air_temp_c"]))
            if "fan_rpm" in readings:
                fan_speed.labels(unit_id=unit_id).set(float(readings["fan_rpm"]))
            if "alarm" in readings:
                unit_alarm.labels(unit_id=unit_id).set(float(readings["alarm"]))
        except (ValueError, KeyError) as err:
            log.warning(f"Skipping unit {unit_id}: {err}")
            continue

def poll_worker():
    """Background thread that periodically fetches and updates metrics."""
    log.info(f"Poll worker started (interval={POLL_INTERVAL}s)")
    
    while state["running"]:
        try:
            payload = fetch_data()
            if payload:
                update_gauges(payload)
                state["last_success_ts"] = int(time.time())
                state["last_error"] = None
        except Exception as err:
            state["last_error"] = str(err)
            log.error(f"Poll cycle failed: {err}")
        
        time.sleep(POLL_INTERVAL)
    
    log.info("Poll worker stopped")

@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/healthz")
def healthz():
    """Kubernetes-style health check."""
    now = int(time.time())
    staleness = now - state["last_success_ts"]
    threshold = POLL_INTERVAL * 4
    
    healthy = staleness < threshold
    status_code = 200 if healthy else 503
    
    return {
        "healthy": healthy,
        "staleness_seconds": staleness,
        "last_error": state["last_error"],
        "threshold_seconds": threshold
    }, status_code

def shutdown_handler(signum, frame):
    """Graceful shutdown on SIGTERM/SIGINT."""
    log.info(f"Received signal {signum}, shutting down...")
    state["running"] = False
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    
    log.info(f"Starting cooling exporter on {LISTEN_HOST}:{LISTEN_PORT}")
    log.info(f"Data source: {'REST API' if COOLING_API_URL else 'Local file'}")
    
    worker = threading.Thread(target=poll_worker, daemon=True)
    worker.start()
    
    app.run(host=LISTEN_HOST, port=LISTEN_PORT, threaded=True)
