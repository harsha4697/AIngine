import requests
import time
import os

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000"
# NOTE: Using raw string r"..." for path with spaces
PROJECT_ROOT = r"/media/harsha4697/Ubuntu B/nBall_Projects/AIngine/backend"
TARGET_MODEL_DIR = "models/Mistral-Small-24B-Instruct-2501-AWQ" # Check this matches your folder
MODEL_PATH = os.path.join(PROJECT_ROOT, TARGET_MODEL_DIR)

MODEL_ID = "Mistral-Master-Test"

def print_header(msg):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")

# 1. LOAD MODEL
def step_1_load():
    print_header("STEP 1: LOADING MODEL (The Engine)")
    print(f"📂 Path: {MODEL_PATH}")
    
    start = time.time()
    payload = {
        "model_id": MODEL_ID,
        "model_path": MODEL_PATH,
        "quantization": "awq"
    }
    try:
        resp = requests.post(f"{BASE_URL}/admin/load-model", json=payload)
        if resp.status_code == 200:
            print(f"✅ Model Loaded Successfully! ({time.time() - start:.2f}s)")
        else:
            print(f"❌ Load Failed: {resp.text}")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ CRITICAL: Is Uvicorn running? Connection refused.")
        exit(1)

# 2. GENERATE (GPU)
def step_2_gpu_generate():
    print_header("STEP 2: GENERATE (Expect GPU 🐢)")
    prompt = "What is the speed of light in vacuum?"
    
    start = time.time()
    payload = {"prompt": prompt, "max_tokens": 50}
    resp = requests.post(f"{BASE_URL}/generate", json=payload)
    duration = time.time() - start
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"🔹 Response: {data['response'][:60]}...")
        print(f"🔹 Source:   {data.get('source')} (Should be 'gpu')")
        print(f"🔹 Time:     {duration:.4f}s")
    else:
        print(f"❌ Error: {resp.text}")

# 3. GENERATE (CACHE)
def step_3_cache_generate():
    print_header("STEP 3: CACHE HIT (Expect Cache ⚡)")
    # Using the EXACT same prompt as Step 2
    prompt = "What is the speed of light in vacuum?"
    
    start = time.time()
    payload = {"prompt": prompt, "max_tokens": 50}
    resp = requests.post(f"{BASE_URL}/generate", json=payload)
    duration = time.time() - start
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"🔹 Response: {data['response'][:60]}...")
        print(f"🔹 Source:   {data.get('source')} (Should be 'cache')")
        print(f"🔹 Time:     {duration:.4f}s")
        
        if data.get('source') == 'cache ⚡':
            print("\n🎉 SUCCESS: The system remembered the answer!")
        else:
            print("\n⚠️ WARNING: Still hit GPU. Did the background task finish saving?")
    else:
        print(f"❌ Error: {resp.text}")

# --- EXECUTION ---
if __name__ == "__main__":
    step_1_load()
    step_2_gpu_generate()
    # Wait a moment for background task to save to DB
    print("\n⏳ Waiting 2 seconds for background DB save...")
    time.sleep(2)
    step_3_cache_generate()