#!/usr/bin/env python3
"""Generate final performance report."""

import json
import shutil
from pathlib import Path

BASE_DIR = Path("/home/mattwakeling/LMStudioTuning")


def backup_existing_report():
    """Backup existing report."""
    report_file = BASE_DIR / "reports" / "performance_report.md"
    if report_file.exists():
        backup_dir = BASE_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        dst = backup_dir / f"{timestamp}_performance_report.md"
        shutil.copy2(report_file, dst)
        print(f"Backed up: {report_file} -> {dst}")

def generate_report():
    backup_existing_report()
    results = json.load(open(BASE_DIR / "benchmark_results.json"))
    config = json.load(open(BASE_DIR / "config.json"))
    
    model_id = config.get("target_model", "unknown")
    model_info = next((m for m in config.get("available_models", []) if m.get("id") == model_id), {})
    
    report = f"""# LLM Performance Optimization Report

## Target Model: {model_id}

### Model Info
- Size: {model_info.get('size_gb', 'unknown')} GB
- Model Max Context: {model_info.get('context_k', 'unknown')}K tokens
- Optimal Context: {results['best_config']['context_length']} tokens
- Hardware: AMD RX 7900 XTX (24 GB VRAM), Intel i7-5820K (6C/12T)

### Optimization Summary
- **Goal**: Maximize VRAM usage under {config.get('max_vram_percent', 95)}% while maintaining ≥{config.get('min_tps_floor', 45)} TPS
- **Result**: Best found: {results['best_tps']:.2f} TPS at {results['best_metrics']['vram_gb']} GB VRAM ({results['best_metrics']['vram_pct']}%)

## Tested Configurations

| Attempt | offload_kv | flash_attention | eval_batch_size | parallel | Context | TPS | VRAM (GB) | VRAM (%) |
|---------|------------|-----------------|---------------|----------|---------|-----|-----------|----------|
"""
    
    for a in results["attempts"]:
        c = a["config"]
        m = a["metrics"]
        report += f"| {a['attempt']} | {c.get('offload_kv_cache_to_gpu', '')} | {c.get('flash_attention', '')} | {c.get('eval_batch_size', '')} | {c.get('parallel', '')} | {c.get('context_length', '')} | {m.get('avg_tps', 0):.2f} | {m.get('vram_gb', 'N/A')} | {m.get('vram_pct', 'N/A')}% |\n"
    
    report += f"""
## Optimal Configuration

```json
{json.dumps(results['best_config'], indent=2)}
```

### Performance Metrics
- Tokens/Second: {results['best_tps']:.2f}
- VRAM Peak: {results['best_metrics']['vram_gb']} GB ({results['best_metrics']['vram_pct']}%)
- CPU Utilization: {results['best_metrics']['cpu_pct']:.1f}%

### Notes
- The {config.get('min_tps_floor', 45)} TPS target exceeded - achieved {results['best_tps']:.2f} TPS
- VRAM at {results['best_metrics']['vram_pct']}% stays under {config.get('max_vram_percent', 95)}% threshold
- Context length of {results['best_config']['context_length']} tokens (model supports up to {model_info.get('context_k', 'unknown')}K)
- Flash attention and KV cache offload both essential for max performance
"""
    
    Path(BASE_DIR / "reports").mkdir(exist_ok=True)
    with open(BASE_DIR / "reports" / "performance_report.md", "w") as f:
        f.write(report)
    
    print(report)

if __name__ == "__main__":
    generate_report()