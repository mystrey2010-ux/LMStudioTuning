#!/usr/bin/env python3
"""List all available LLM models in LM Studio."""

import lmstudio
import json

def list_models():
    client = lmstudio.Client("192.168.50.2:1234")
    
    for m in client.list_downloaded_models():
        if m.type == "llm":
            info = m.info
            size_bytes = info.size_bytes if hasattr(info, 'size_bytes') else 0
            max_ctx = info.max_context_length if hasattr(info, 'max_context_length') else 0
            print(json.dumps([{"id": m.model_key, "size_gb": round(size_bytes / 1e9, 1), "context_k": max_ctx // 1024}]))

if __name__ == "__main__":
    list_models()
