# LM Studio Configuration Report for qwen/qwen3-coder-30b

## Model Information
- **Model**: qwen/qwen3-coder-30b
- **Host**: 192.168.50.2:1234
- **Status**: Loaded (based on applied configuration)

## Configuration Parameters

### General Settings
- **target_model**: qwen/qwen3-coder-30b
- **max_vram_percent**: 95
- **min_tps_floor**: 45
- **inference_timeout_seconds**: 600
- **load_timeout_seconds**: 600
- **iterations_per_config**: 1

### Batch Sizes
- **Batch Sizes**: [2048]

### Parallel Values
- **Parallel Values**: [1]

### GPU Layers
- **GPU Layers**: ['max']

### Thread Counts
- **Thread Counts**: [6]

### Rope Scaling
- **Rope Scaling**: ['none']

### Mirostat
- **Mirostat**: [0]

## Applied Configuration (Current Runtime Settings)

- **context_length**: 65536
- **eval_batch_size**: 2048
- **parallel**: 1
- **flash_attention**: True
- **offload_kv_cache_to_gpu**: True
- **num_experts**: None
- **llama_k_cache_quantization_type**: q8_0
- **llama_v_cache_quantization_type**: q8_0
- **gpu_layers**: None
- **thread_count**: 6
- **rope_scaling_type**: None
- **mirostat**: 0

## Inference Settings

- **Context Length**: 65536
- **Eval Batch Size**: 2048
- **Thread Count**: 6
- **Parallel**: 1
- **Flash Attention**: True
- **Offload KV Cache to GPU**: True

## Quantization Settings
- **LLaMA K Cache Quantization Type**: q8_0
- **LLaMA V Cache Quantization Type**: q8_0

## Sampling Parameters

Sampling parameters not found in Windows filesystem. 
Showing default values typically used with this model:

- **Temperature**: 0.7
- **Top K**: 40
- **Repeat Penalty**: 1.1
- **Presence Penalty**: 0.0
- **Top P**: 0.9
- **Min P**: 0.0

To get actual UI values, ensure the Windows filesystem is accessible via /mnt/c/ mount.
## System Information
- **Platform**: Linux-6.18.33.1-microsoft-standard-WSL2-x86_64-with-glibc2.43
- **Python Version**: 3.10.20
- **CPU Count**: 12
- **Memory Total**: 31.3 GB
- **LM Studio SDK Version**: 1.5.0

## Notes
This configuration represents the current applied settings for the qwen/qwen3-coder-30b model in this LM Studio environment.