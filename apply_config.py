#!/usr/bin/env python3
"""Apply optimal configuration to LM Studio and save for reuse."""

import json
import requests
import os

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://192.168.50.2:1234")
BASE_DIR = "/home/mattwakeling/LMStudioTuning"

def apply_config():
    results = json.load(open(f"{BASE_DIR}/benchmark_results.json"))
    best_config = results.get("best_config")
    
    if not best_config:
        print("No configuration found")
        return
    
    model_id = json.load(open(f"{BASE_DIR}/config.json"))["target_model"]
    
    print(f"Applying config to LM Studio for {model_id}:")
    print(json.dumps(best_config, indent=2))
    
    # Load with optimal config
    resp = requests.post(f"{LM_STUDIO_URL}/api/v1/models/load",
        json={"model": model_id, **best_config})
    
    status = resp.json().get("status")
    if status == "loaded":
        print(f"\nModel loaded successfully with optimal configuration!")
        print(f"Instance: {resp.json().get('instance_id')}")
        # Save applied config for future reloads
        with open(f"{BASE_DIR}/applied_config.json", "w") as f:
            json.dump({"model": model_id, **best_config}, f, indent=2)
        print(f"Saved to: {BASE_DIR}/applied_config.json")
    else:
        print(f"Load failed: {resp.json()}")

if __name__ == "__main__":
    apply_config()