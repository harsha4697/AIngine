import requests
import time

BASE_URL = "http://localhost:8000"
PROMPT = "What are the benefits of eating apples?"

def generate(label):
    print(f"\n--- {label} ---")
    start = time.time()
    payload = {"prompt": PROMPT, "max_tokens": 100}
    
    try:
        resp = requests.post(f"{BASE_URL}/generate", json=payload)
        duration = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            source = data.get('source', 'unknown')
            print(f"✅ Status: 200 OK")
            print(f"🔌 Source: {source}")
            print(f"⏱️  Time:   {duration:.4f}s")
            print(f"📝 Output: {data['response'][:60]}...")
            return source
        else:
            print(f"❌ Error {resp.status_code}: {resp.text}")
            return "error"
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return "error"

print(f"🚀 TESTING SEMANTIC CACHE")

# 1. Cold Request
s1 = generate("Request 1 (Expecting GPU 🐢)")

if s1 == "error":
    print("\n⚠️  Did you forget to load a model first? Run test_sprint1.py!")
    exit(1)

# 2. Wait a moment for Background Task to finish saving to DB
print("\n...waiting for background DB write...")
time.sleep(1) 

# 3. Warm Request
s2 = generate("Request 2 (Expecting CACHE ⚡)")

print("\n" + "="*30)
if s1.startswith("gpu") and s2.startswith("cache"):
    print("✅ SUCCESS: Cache hit on second try!")
else:
    print("❌ FAILURE: Caching did not work as expected.")