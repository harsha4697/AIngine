import requests
import time
import os

# CONFIGURATION
BASE_URL = "http://localhost:8000"

# --- PATH CONFIGURATION ---
# NOTE: Using raw string r"..." to ensure the space in "Ubuntu B" is handled correctly
PROJECT_ROOT = r"/media/harsha4697/Ubuntu B/nBall_Projects/AIngine/backend"

# TARGET MODEL: Mistral 24B AWQ
# This is relative to the PROJECT_ROOT
TARGET_MODEL_DIR = "models/Mistral-Small-24B-Instruct-2501-AWQ"

# Construct the full absolute path
MODEL_PATH = os.path.join(PROJECT_ROOT, TARGET_MODEL_DIR)

# Test Identifiers
MODEL_ID_1 = "Mistral-24B-Session-1"
MODEL_ID_2 = "Mistral-24B-Session-2" 

def print_header(msg):
    print(f"\n{'='*50}\n{msg}\n{'='*50}")

def check_health():
    print(f"📡 Connecting to {BASE_URL}...")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health OK: {resp.json()}")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        print("💡 Hint: Make sure 'uvicorn main:app' is running in another terminal.")
        exit(1)

def load_model(model_id, path):
    print(f"⏳ Requesting Load: {model_id}")
    print(f"   📂 Path: {path}")
    start = time.time()
    payload = {
        "model_id": model_id,
        "model_path": path,
        "quantization": "awq"
    }
    resp = requests.post(f"{BASE_URL}/admin/load-model", json=payload)
    
    if resp.status_code == 200:
        print(f"✅ Loaded successfully in {time.time() - start:.2f}s")
    else:
        print(f"❌ Load Failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        exit(1)

def generate_text(prompt):
    print(f"📝 Generating text for prompt: '{prompt}'")
    payload = {"prompt": prompt, "max_tokens": 100}
    start = time.time()
    resp = requests.post(f"{BASE_URL}/generate", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print(f"🔹 Response ({time.time() - start:.2f}s):")
        print(f"   {data['response']}")
    else:
        print(f"❌ Generation Failed: {resp.text}")

# --- EXECUTION FLOW ---
print_header(f"STARTING SPRINT 1 SMOKE TEST\nTarget: {TARGET_MODEL_DIR}")

# 1. Check Server
check_health()

# 2. Load Model First Time
print_header("STEP 1: Load Mistral 24B")
load_model(MODEL_ID_1, MODEL_PATH)
generate_text("Explain quantum computing in one sentence.")

# 3. Force Swap (Simulating a change)
print_header("STEP 2: Triggering Swap (VRAM Cleanup Test)")
print("ℹ️  Watch your Uvicorn terminal for 'VRAM cleared' message.")
load_model(MODEL_ID_2, MODEL_PATH)

# 4. Generate with 'New' Model
generate_text("What is the capital of India?")

print_header("TEST COMPLETE")