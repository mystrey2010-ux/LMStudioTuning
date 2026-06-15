# LLM Performance Optimizer for LM Studio

## Configuration Report Generation

```bash
# Generate comprehensive LM Studio configuration report for current model
python /home/mattwakeling/LMStudioTuning/regenerate_lmstudio_report.py
```

This generates `lmstudio_config_report.md` containing all configuration parameters, runtime settings, inference settings, and sampling parameters for the qwen/qwen3-coder-30b model.

## Setup

### Create Conda Environment
```bash
conda create -n llm_optimizer python=3.10 -y
conda activate llm_optimizer
pip install requests psutil lmstudio
```

## Usage

```bash
# Run full matrix optimization search with checkpointing
python /home/mattwakeling/LMStudioTuning/llm_optimizer.py

# Generate detailed performance report
python /home/mattwakeling/LMStudioTuning/generate_report.py

# Apply optimal configuration to LM Studio
python /home/mattwakeling/LMStudioTuning/apply_config.py

# List available models in LM Studio
python /home/mattwakeling/LMStudioTuning/list_models.py
```

## Configuration (config.json)

- `target_model`: Model to optimize
- `max_vram_percent`: VRAM limit (default: 95%)
- `min_tps_floor`: Minimum TPS target (default: 45)
- `inference_timeout_seconds`: Request timeout
- `load_timeout_seconds`: Model loading timeout
- `iterations_per_config`: Number of iterations per config test
- `expert_counts`: List of expert counts to test (use "false" to skip)
- `kv_cache_types`: KV cache quantization types to test
- `batch_sizes`: Batch sizes to test
- `parallel_values`: Parallel processing values to test
- `gpu_layers`: GPU layers to test (supports "max")
- `thread_counts`: Thread counts to test
- `rope_scaling`: Rope scaling types to test
- `mirostat`: Mirostat values to test

## Key Features

- Full matrix search through multiple configuration parameters
- Checkpointing capability to resume from where it left off
- Comprehensive performance monitoring and reporting
- Automatic backup of previous runs
- Optimal configuration application to LM Studio

## Output Files

- `benchmark_results.json` - Detailed performance data with all test results
- `backups/` - Timestamped backups of previous runs (results and reports)
- `reports/performance_report.md` - Markdown report with detailed analysis and optimal configuration
- `applied_config.json` - Optimal configuration applied to LM Studio for reuse
- `lmstudio_config_report.md` - Configuration parameters and settings for the loaded model (regenerable)