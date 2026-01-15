#!/usr/bin/env python3
"""
Generate Prometheus file_sd targets from inventory CSV.

Reads datacenter inventory and produces JSON target files for:
- node_exporter (OS metrics)
- dcgm-exporter (GPU metrics)  
- ipmi_exporter (BMC/OOB)
- snmp_exporter (network gear, PDUs)
"""
import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

def parse_args():
    p = argparse.ArgumentParser(description="Generate Prometheus file_sd targets from inventory")
    p.add_argument("inventory", help="Path to inventory CSV file")
    p.add_argument("output_dir", help="Directory to write target JSON files")
    p.add_argument("--node-port", default="9100", help="node_exporter port (default: 9100)")
    p.add_argument("--dcgm-port", default="9400", help="dcgm-exporter port (default: 9400)")
    return p.parse_args()

def read_inventory(csv_path: str) -> List[Dict[str, str]]:
    """Read and validate inventory CSV."""
    required_cols = {"host", "mgmt_ip", "dc", "row", "rack", "cell"}
    
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                log.error(f"Empty inventory: {csv_path}")
                sys.exit(1)
            
            missing = required_cols - set(rows[0].keys())
            if missing:
                log.error(f"Missing required columns: {missing}")
                sys.exit(1)
            
            log.info(f"Loaded {len(rows)} hosts from {csv_path}")
            return rows
    
    except FileNotFoundError:
        log.error(f"Inventory not found: {csv_path}")
        sys.exit(1)
    except csv.Error as err:
        log.error(f"CSV parse error: {err}")
        sys.exit(1)

def build_targets(inventory: List[Dict[str, str]], node_port: str, dcgm_port: str):
    """Build target lists for each exporter type."""
    node_tgts = []
    dcgm_tgts = []
    bmc_tgts = []
    snmp_tgts = []
    
    for row in inventory:
        base_labels = {
            "host": row["host"],
            "dc": row["dc"],
            "row": row["row"],
            "rack": row["rack"],
            "cell": row["cell"]
        }
        
        mgmt_ip = row["mgmt_ip"].strip()
        if not mgmt_ip:
            log.warning(f"Skipping host {row['host']}: no mgmt_ip")
            continue
        
        # Node and DCGM run on the host
        node_tgts.append({
            "targets": [f"{mgmt_ip}:{node_port}"],
            "labels": base_labels
        })
        dcgm_tgts.append({
            "targets": [f"{mgmt_ip}:{dcgm_port}"],
            "labels": base_labels
        })
        
        # BMC uses multi-target exporter pattern
        bmc_ip = row.get("bmc_ip", "").strip()
        if bmc_ip:
            bmc_tgts.append({
                "targets": [bmc_ip],
                "labels": base_labels
            })
        
        # SNMP devices (semicolon-separated list)
        snmp_devices = row.get("snmp_devices", "").strip()
        if snmp_devices:
            for device in snmp_devices.split(";"):
                device = device.strip()
                if device:
                    snmp_tgts.append({
                        "targets": [device],
                        "labels": {
                            "dc": row["dc"],
                            "row": row["row"],
                            "rack": row["rack"]
                        }
                    })
    
    return {
        "node_targets.json": node_tgts,
        "dcgm_targets.json": dcgm_tgts,
        "bmc_targets.json": bmc_tgts,
        "snmp_targets.json": snmp_tgts
    }

def write_targets(output_dir: str, targets: Dict[str, List[Dict[str, Any]]]):
    """Write target files to output directory."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    for filename, data in targets.items():
        target_file = out_path / filename
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        log.info(f"Wrote {len(data)} targets to {target_file}")

def main():
    args = parse_args()
    inventory = read_inventory(args.inventory)
    targets = build_targets(inventory, args.node_port, args.dcgm_port)
    write_targets(args.output_dir, targets)
    log.info("Target generation complete")

if __name__ == "__main__":
    main()
