from app.services.embedding_service import embedding_service
import time

print("--- Testing Embedding Service ---")

# 1. Initialize (First run downloads the model ~90MB)
start = time.time()
embedding_service.initialize()
print(f"Initialization took: {time.time() - start:.4f}s")

# 2. Generate Vector
text = "What is the capital of France?"
start = time.time()
vector = embedding_service.embed_text(text)
duration = time.time() - start

print(f"Vector Dimensions: {len(vector)} (Should be 384)")
print(f"Inference Time: {duration:.4f}s")
print(f"First 5 floats: {vector[:5]}")

if len(vector) == 384:
    print("✅ TEST PASSED")
else:
    print("❌ TEST FAILED: Wrong dimensions")