import gc
import torch
from vllm import LLM, SamplingParams
# specialized cleanup for vLLM's backend
from vllm.distributed.parallel_state import destroy_model_parallel 
from typing import Optional

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.llm = None
            cls._instance.current_model_name = None
        return cls._instance

    def unload_model(self):
        """
        CRITICAL: Forcefully cleans up GPU memory.
        """
        if self.llm:
            print(f"🛑 Unloading model: {self.current_model_name}...")
            
            # 1. Destroy the vLLM distributed process group (Critical for VRAM release)
            try:
                destroy_model_parallel()
            except Exception:
                pass # Ignore if not initialized
                
            # 2. Delete the object reference
            del self.llm
            self.llm = None
            self.current_model_name = None
            
            # 3. Force Python Garbage Collection
            gc.collect()
            
            # 4. Clear CUDA Cache (The VRAM Surgeon)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            
            print("✅ VRAM cleared.")
        else:
            print("Model is already empty.")

    def load_model(self, model_path: str, model_id: str, quantization: Optional[str] = "awq"):
        """
        Loads a new model. If one exists, it unloads it first.
        """
        # 1. Check if we need to swap
        if self.llm:
            if self.current_model_name == model_id:
                print(f"Model {model_id} already loaded.")
                return
            else:
                self.unload_model()

        print(f"🚀 Loading model: {model_id} from {model_path}...")
        
        # 2. Initialize vLLM
        try:
            # Lowered util slightly to 0.85 to leave room for your OS + Embedding Model
            self.llm = LLM(
                model=model_path,
                quantization=quantization, 
                dtype="auto", # auto is safer than float16 for quantized models
                gpu_memory_utilization=0.85, 
                trust_remote_code=True,
                enforce_eager=True, # Helps with cleanup, slightly slower but safer for swapping
                max_model_len=8192  # <--- CRITICAL FIX: Limits context window to prevent VRAM OOM on Llama 3.1
            )
            self.current_model_name = model_id
            print(f"✅ {model_id} successfully loaded onto GPU.")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            # Ensure cleanup happens even if load fails
            self.unload_model()
            raise e

    def generate(self, prompt: str, max_tokens=200):
        if not self.llm:
            raise RuntimeError("No model loaded. Please load a model first.")
        
        model_id = self.current_model_name.lower()
        formatted_prompt = prompt # Default fallback

        # --- STRATEGY: MANUAL TEMPLATING ---
        # We manually build the string to ensure the "System Prompt" is included.
        # This fixes the "Karen" bug by forcing the AI to be an assistant.

        # 1. MISTRAL (The "Hi" Fix)
        # Format: <s>[INST] System Instruction + User Prompt [/INST]
        if "mistral" in model_id:
            formatted_prompt = (
                f"<s>[INST] You are a helpful AI assistant. "  # <--- Hidden System Prompt
                f"{prompt} [/INST]"
            )

        # 2. LLAMA 3.1 / 3.3
        # Format: <|begin_of_text|><|start_header_id|>system...
        elif "llama" in model_id:
            formatted_prompt = (
                f"<|begin_of_text|>"
                f"<|start_header_id|>system<|end_header_id|>\n\nYou are a helpful AI assistant.<|eot_id|>" # <--- Hidden System Prompt
                f"<|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            )

        # 3. QWEN / GEMMA / OTHERS (Use Auto-Tokenizer)
        else:
            try:
                tokenizer = self.llm.get_tokenizer()
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant."}, # <--- Hidden System Prompt
                    {"role": "user", "content": prompt}
                ]
                formatted_prompt = tokenizer.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
            except Exception as e:
                print(f"⚠️ Template Error: {e}")
                # Ultimate Fallback
                formatted_prompt = f"System: You are a helpful assistant.\nUser: {prompt}\nAssistant:"

        print(f"📝 PROMPT SENT TO GPU ({model_id}):\n{formatted_prompt}") # Check your logs to see this!

        # --- GENERATE ---
        params = SamplingParams(temperature=0.7, max_tokens=max_tokens)
        outputs = self.llm.generate([formatted_prompt], params)
        return outputs[0].outputs[0].text

# Global instance
model_manager = ModelManager()