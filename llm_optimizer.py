#!/usr/bin/env python3
"""LLM Performance Optimizer using LM Studio SDK - Full Matrix Search with Checkpointing."""

import json
import subprocess
import time
import shutil
from pathlib import Path
from typing import Optional
import os

import psutil
import lmstudio

LM_STUDIO_HOST = os.getenv("LM_STUDIO_HOST", "192.168.50.2:1234")
PROMPT = "Explain quantum computing in 200 words, covering qubits, superposition, and applications."
MAX_TOKENS = 200

BASE_DIR = Path("/home/mattwakeling/LMStudioTuning")
GPU_SCRIPT = Path.home() / ".hermes/hermes-agent/skills/mlops/amd-gpu-monitor/scripts/gpu_monitor.py"

config = json.load(open(BASE_DIR / "config.json"))
TARGET_MODEL = config["target_model"]
MAX_VRAM_PCT = config["max_vram_percent"]
MIN_TPS_FLOOR = config["min_tps_floor"]
ITERATIONS = config["iterations_per_config"]
KV_CACHE_TYPES = config["kv_cache_types"]
BATCH_SIZES = config["batch_sizes"]
PARALLEL_VALUES = config["parallel_values"]
EXPERT_COUNTS = config["expert_counts"]
# Handle special case where "false" means don't set the expert count parameter
if EXPERT_COUNTS == ["false"]:
    EXPERT_COUNTS = [None]  # Set to None to indicate no expert count testing
# Handle special case where "false" means don't test this parameter
if EXPERT_COUNTS == ["false"]:
    EXPERT_COUNTS = [None]  # Set to None to indicate no expert testing
elif isinstance(EXPERT_COUNTS, list) and "false" in EXPERT_COUNTS:
    # Remove "false" from the list and keep others
    EXPERT_COUNTS = [x for x in EXPERT_COUNTS if x != "false"]
    if not EXPERT_COUNTS:  # If list becomes empty after removing "false"
        EXPERT_COUNTS = [None]
GPU_LAYERS = config.get("gpu_layers", [0, 16, 32, 48, "max"])
THREAD_COUNTS = config.get("thread_counts", [4, 8, 16, 24, 32])
ROPE_SCALING = config.get("rope_scaling", ["none", "linear", "dynamic"])
MIROSTAT = config.get("mirostat", [0, 1, 2])


def log(msg):
    print(msg)
    import sys
    sys.stdout.flush()


def get_gpu() -> Optional[dict]:
    try:
        r = subprocess.run(["python3", str(GPU_SCRIPT)], capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            d = json.loads(r.stdout)
            return d.get("data") if d.get("success") else None
    except:
        pass
    return None


def unload_all(client):
    for m in client.list_loaded_models():
        try:
            m.unload()
        except:
            pass


def run_inference(model) -> Optional[dict]:
    tps_values = []
    for _ in range(ITERATIONS):
        try:
            start = time.perf_counter()
            result = model.respond(PROMPT, config={"maxTokens": MAX_TOKENS, "temperature": 0.7})
            duration = time.perf_counter() - start
            tokens = len(result.content.split()) if result.content else 0
            tps_values.append(tokens / duration if duration > 0 else 0)
        except Exception as e:
            log(f"    Error: {e}")
            break
    
    if not tps_values:
        return None
    
    gpu = get_gpu()
    return {
        "avg_tps": sum(tps_values) / len(tps_values),
        "vram_gb": gpu.get("VRAMUsedGB") if gpu else None,
        "vram_pct": gpu.get("UtilizationPercent") if gpu else None,
        "cpu_pct": psutil.cpu_percent(interval=0.1),
    }


def backup_files():
    files = ["benchmark_results.json", "reports/performance_report.md"]
    backup_dir = BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    for f in files:
        src = BASE_DIR / f
        if src.exists():
            shutil.copy2(src, backup_dir / f"{timestamp}_{f.replace('/', '_')}")


def save_checkpoint(results, completed_configs):
    checkpoint = {"completed_configs": list(completed_configs)}
    with open(BASE_DIR / "checkpoint.json", "w") as f:
        json.dump(checkpoint, f, indent=2)
    with open(BASE_DIR / "benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)


def main():
    backup_files()
    client = lmstudio.Client(LM_STUDIO_HOST)
    
    max_ctx = 262144
    try:
        for m in client.list_downloaded_models():
            if m.model_key == TARGET_MODEL and hasattr(m.info, 'max_context_length'):
                max_ctx = m.info.max_context_length
                break
    except:
        pass
    candidates = [max_ctx // 4, max_ctx // 2, max_ctx]
    context_lengths = sorted(set(c for c in candidates if c >= 8192))
    total = len(context_lengths) * len(BATCH_SIZES) * len(PARALLEL_VALUES) * len(EXPERT_COUNTS) * len(KV_CACHE_TYPES) * len(GPU_LAYERS) * len(THREAD_COUNTS) * len(ROPE_SCALING) * len(MIROSTAT)
    
    log(f"Target: {TARGET_MODEL}")
    log(f"Max context: {max_ctx}, Testing lengths: {context_lengths}")
    log(f"Total combinations to test: {total}")
    
    checkpoint_file = BASE_DIR / "checkpoint.json"
    completed_configs = set()
    results = {"attempts": [], "best_tps": 0, "best_config": None, "best_metrics": None}
    
    if checkpoint_file.exists():
        try:
            checkpoint = json.load(open(checkpoint_file))
            completed_configs = set(checkpoint.get("completed_configs", []))
            log(f"Resuming from checkpoint: {len(completed_configs)} configs already tested")
        except:
            pass
    
    unload_all(client)
    time.sleep(1)
    
    attempt = len(completed_configs)
    for ctx in context_lengths:
        for batch in BATCH_SIZES:
            for par in PARALLEL_VALUES:
                for experts in EXPERT_COUNTS:
                    for kv_type in KV_CACHE_TYPES:
                        for gpu_l in GPU_LAYERS:
                            for thread in THREAD_COUNTS:
                                for rope in ROPE_SCALING:
                                    for miro in MIROSTAT:
                                        kv_val = None if kv_type == "false" else kv_type
                                        gpu_val = None if gpu_l == "max" else gpu_l
                                        rope_val = None if rope == "none" else rope
                                        cfg_key = f"{ctx}_{batch}_{par}_{experts}_{kv_type}_{gpu_l}_{thread}_{rope}_{miro}"
                                        
                                        if cfg_key in completed_configs:
                                            log(f"  Skipping already tested: {cfg_key}")
                                            continue
                                        
                                        attempt += 1
                                        log(f"  UNIQUE attempt: {cfg_key}")
                                        completed_configs.add(cfg_key)
                                        
                                        cfg = {
                                            "contextLength": ctx,
                                            "evalBatchSize": batch,
                                            "parallel": par,
                                            "flashAttention": True,
                                            "offloadKVCacheToGpu": True,
                                            "llamaKCacheQuantizationType": kv_val,
                                            "llamaVCacheQuantizationType": kv_val,
                                            "gpuLayers": gpu_val,
                                            "threadCount": thread,
                                            "ropeScalingType": rope_val,
                                            "mirostat": miro
                                        }
                                        
                                        # Only set numExperts if it's not None (when "false" was specified)
                                        if experts is not None:
                                            cfg["numExperts"] = experts
                                        
                                        log(f"\n--- Attempt {attempt}/{total} ---")
                                        log(f"Config: ctx={ctx}, batch={batch}, par={par}, experts={experts}, kv={kv_type}, gpu={gpu_l}, thread={thread}, rope={rope}, miro={miro}")
                                        
                                        try:
                                            model = client.llm.load_new_instance(TARGET_MODEL, config=cfg)
                                            log(f"  Loaded, running inference...")
                                            time.sleep(3)
                                            
                                            metrics = run_inference(model)
                                            if metrics:
                                                saved_cfg = {
                                                    "context_length": ctx,
                                                    "eval_batch_size": batch,
                                                    "parallel": par,
                                                    "flash_attention": True,
                                                    "offload_kv_cache_to_gpu": True,
                                                    "num_experts": experts,
                                                    "llama_k_cache_quantization_type": kv_val,
                                                    "llama_v_cache_quantization_type": kv_val,
                                                    "gpu_layers": gpu_val,
                                                    "thread_count": thread,
                                                    "rope_scaling_type": rope_val,
                                                    "mirostat": miro
                                                }
                                                results["attempts"].append({"attempt": attempt, "config": saved_cfg, "metrics": metrics})
                                                log(f"  TPS: {metrics['avg_tps']:.2f}, VRAM: {metrics['vram_gb']}GB ({metrics['vram_pct']}%)")
                                                
                                                if metrics["avg_tps"] > results["best_tps"]:
                                                    results["best_tps"] = metrics["avg_tps"]
                                                    results["best_config"] = saved_cfg
                                                    results["best_metrics"] = metrics
                                                    log(f"  *** New best! ***")
                                                
                                                save_checkpoint(results, completed_configs)
                                            try:
                                                model.unload()
                                            except:
                                                pass
                                        except Exception as e:
                                            log(f"  Load error: {e}")
                                            save_checkpoint(results, completed_configs)
    
    checkpoint_file.unlink(missing_ok=True)
    
    log(f"\n{'='*50}")
    log(f"FINAL: Best TPS = {results['best_tps']:.2f}")
    if results.get("best_config"):
        for k, v in results["best_config"].items():
            log(f"  {k}: {v}")
        with open(BASE_DIR / "applied_config.json", "w") as f:
            json.dump({"model": TARGET_MODEL, **results["best_config"]}, f, indent=2)


if __name__ == "__main__":
    main()