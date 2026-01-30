import requests
import time
import os

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000"

# 🛑 FIX: Use the EXACT folder name from your screenshot (No -AWQ suffix)
TARGET_MODEL_DIR = "models/Meta-Llama-3.1-8B-Instruct" 

PROJECT_ROOT = r"/media/harsha4697/Ubuntu B/nBall_Projects/AIngine/backend"
MODEL_PATH = os.path.join(PROJECT_ROOT, TARGET_MODEL_DIR)

def run_test():
    print(f"🚀 TESTING LLAMA 8B (Standard Weights)")
    print(f"📂 Path: {MODEL_PATH}")

    # 1. Load
    start = time.time()
    # We send quantization=None because this is a standard .safetensors model
    resp = requests.post(f"{BASE_URL}/admin/load-model", json={
        "model_id": "llama-8b-standard",
        "model_path": MODEL_PATH,
        "quantization": None 
    })
    
    if resp.status_code != 200:
        print(f"❌ Load Failed: {resp.text}")
        return

    print(f"✅ Loaded in {time.time() - start:.2f}s")

    # 2. Generate
    resp = requests.post(f"{BASE_URL}/generate", json={
        "prompt": "Hello Llama! Who are you?",
        "max_tokens": 50
    })
    
    if resp.status_code == 200:
        print(f"🔹 Response: {resp.json()['response']}")
    else:
        print(f"❌ Generation Failed: {resp.text}")

if __name__ == "__main__":
    run_test()