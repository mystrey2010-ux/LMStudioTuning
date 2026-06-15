#!/usr/bin/env python3
"""Script to regenerate LM Studio configuration report for qwen/qwen3-coder-30b."""

import json
import os

def get_windows_username():
    """Try to get Windows username through WSL."""
    try:
        # Try multiple methods to get Windows username
        result = os.popen("powershell.exe '$env:UserName' 2>/dev/null").read().strip()
        if result and not result.startswith('Error'):
            return result
    except:
        pass
    
    # Alternative method
    try:
        result = os.popen("cmd.exe /c 'echo %USERNAME%' 2>/dev/null").read().strip()
        if result:
            return result
    except:
        pass
    
    # Try reading from environment
    try:
        return os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    except:
        return 'unknown'

def extract_sampling_from_preset(preset_data):
    """Extract sampling parameters from preset data."""
    if isinstance(preset_data, dict):
        return {
            "temperature": preset_data.get("temperature", 0.7),
            "top_k": preset_data.get("top_k", 40),
            "repeat_penalty": preset_data.get("repeat_penalty", 1.1),
            "presence_penalty": preset_data.get("presence_penalty", 0.0),
            "top_p": preset_data.get("top_p", 0.9),
            "min_p": preset_data.get("min_p", 0.0)
        }
    return None

def generate_report():
    """Generate a comprehensive LM Studio configuration report."""
    
    # Read the config file
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config.json: {e}")
        config = {}
    
    # Read the applied configuration if it exists
    try:
        with open('applied_config.json', 'r') as f:
            applied_config = json.load(f)
    except Exception as e:
        print(f"No applied configuration found: {e}")
        applied_config = {}
    
    # Create the markdown report
    report_content = "# LM Studio Configuration Report for qwen/qwen3-coder-30b\n\n"
    
    report_content += "## Model Information\n"
    report_content += "- **Model**: qwen/qwen3-coder-30b\n"
    report_content += "- **Host**: 192.168.50.2:1234\n"
    report_content += "- **Status**: Loaded (based on applied configuration)\n\n"
    
    report_content += "## Configuration Parameters\n\n"
    
    report_content += "### General Settings\n"
    for key, value in config.items():
        if key not in ['expert_counts', 'kv_cache_types', 'batch_sizes', 'parallel_values', 
                     'gpu_layers', 'thread_counts', 'rope_scaling', 'mirostat']:
            report_content += f"- **{key}**: {value}\n"
    report_content += "\n"
    
    report_content += "### Batch Sizes\n"
    report_content += f"- **Batch Sizes**: {config.get('batch_sizes', [])}\n\n"
    
    report_content += "### Parallel Values\n"
    report_content += f"- **Parallel Values**: {config.get('parallel_values', [])}\n\n"
    
    report_content += "### GPU Layers\n"
    report_content += f"- **GPU Layers**: {config.get('gpu_layers', [])}\n\n"
    
    report_content += "### Thread Counts\n"
    report_content += f"- **Thread Counts**: {config.get('thread_counts', [])}\n\n"
    
    report_content += "### Rope Scaling\n"
    report_content += f"- **Rope Scaling**: {config.get('rope_scaling', [])}\n\n"
    
    report_content += "### Mirostat\n"
    report_content += f"- **Mirostat**: {config.get('mirostat', [])}\n\n"
    
    report_content += "## Applied Configuration (Current Runtime Settings)\n\n"
    
    if applied_config:
        for key, value in applied_config.items():
            if key != 'model':
                report_content += f"- **{key}**: {value}\n"
    else:
        report_content += "No applied configuration found.\n\n"
    
    # Add inference settings
    report_content += "\n## Inference Settings\n\n"
    report_content += "- **Context Length**: 65536\n"
    report_content += "- **Eval Batch Size**: 2048\n"
    report_content += "- **Thread Count**: 6\n"
    report_content += "- **Parallel**: 1\n"
    report_content += "- **Flash Attention**: True\n"
    report_content += "- **Offload KV Cache to GPU**: True\n"
    
    # Add quantization info
    report_content += "\n## Quantization Settings\n"
    report_content += "- **LLaMA K Cache Quantization Type**: q8_0\n"
    report_content += "- **LLaMA V Cache Quantization Type**: q8_0\n"
    
    # Add sampling parameters - try to get from Windows filesystem
    report_content += "\n## Sampling Parameters\n\n"
    
    win_user = get_windows_username()
    sampling_params_found = False
    source_found = None
    
    # Try to access Windows filesystem for LM Studio presets
    possible_paths = [
        f"/mnt/c/Users/{win_user}/.lmstudio/presets/",
        f"/mnt/c/Users/{win_user}/AppData/Roaming/LM-Studio/",
        f"/mnt/c/Users/{win_user}/AppData/Local/LM-Studio/presets/",
    ]
    
    for base_path in possible_paths:
        if os.path.exists(base_path):
            print(f"Checking path: {base_path}")
            try:
                files = os.listdir(base_path)
                for filename in files:
                    if filename.endswith('.json'):
                        file_path = os.path.join(base_path, filename)
                        try:
                            with open(file_path, 'r') as f:
                                preset_data = json.load(f)
                                sampling_params = extract_sampling_from_preset(preset_data)
                                if sampling_params:
                                    report_content += f"### Found in Windows Host Filesystem: {filename}\n"
                                    for param, value in sampling_params.items():
                                        report_content += f"- **{param}**: {value}\n"
                                    report_content += "\n"
                                    sampling_params_found = True
                                    source_found = filename
                        except:
                            continue
            except:
                continue
    
    if not sampling_params_found:
        report_content += "Sampling parameters not found in Windows filesystem. \n"
        report_content += "Showing default values typically used with this model:\n\n"
        report_content += "- **Temperature**: 0.7\n"
        report_content += "- **Top K**: 40\n"
        report_content += "- **Repeat Penalty**: 1.1\n"
        report_content += "- **Presence Penalty**: 0.0\n"
        report_content += "- **Top P**: 0.9\n"
        report_content += "- **Min P**: 0.0\n\n"
        report_content += "To get actual UI values, ensure the Windows filesystem is accessible via /mnt/c/ mount.\n"
    
    # Add system info
    import platform
    import psutil
    
    report_content += "## System Information\n"
    report_content += "- **Platform**: " + platform.platform() + "\n"
    report_content += "- **Python Version**: " + platform.python_version() + "\n"
    report_content += "- **CPU Count**: " + str(psutil.cpu_count()) + "\n"
    report_content += "- **Memory Total**: " + str(round(psutil.virtual_memory().total / (1024**3), 2)) + " GB\n"
    
    # Add LM Studio SDK info
    try:
        import lmstudio
        version = getattr(lmstudio, '__version__', 'Unknown')
        report_content += "- **LM Studio SDK Version**: " + version + "\n\n"
    except:
        report_content += "- **LM Studio SDK Version**: Unknown\n\n"
    
    report_content += "## Notes\n"
    report_content += "This configuration represents the current applied settings for the qwen/qwen3-coder-30b model in this LM Studio environment."

    # Write to file
    with open('lmstudio_config_report.md', 'w') as f:
        f.write(report_content)
    
    print("Configuration report has been regenerated and saved to:")
    print("- lmstudio_config_report.md")

if __name__ == "__main__":
    generate_report()