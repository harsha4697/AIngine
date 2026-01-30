export interface ModelConfig {
  id: string;
  name: string;
  path: string;
  description: string;
  vram_estimate: string;
  quantization?: string; // <--- Ensure this is here
}

const BASE_PATH = "/media/harsha4697/Ubuntu B/nBall_Projects/AIngine/backend/models";

export const AVAILABLE_MODELS: ModelConfig[] = [
  {
    id: "qwen-32b",
    name: "Qwen 2.5 (32B)",
    path: `${BASE_PATH}/Qwen2.5-32B-Instruct-AWQ`,
    description: "Best all-rounder. Coding & Logic.",
    vram_estimate: "~18 GB",
    quantization: "awq"
  },
  {
    id: "mistral-24b",
    name: "Mistral Small (24B)",
    path: `${BASE_PATH}/Mistral-Small-24B-Instruct-2501-AWQ`,
    description: "High speed, great reasoning.",
    vram_estimate: "~14 GB",
    quantization: "awq"
  },
  // 👇 THIS IS THE MISSING PART
  {
    id: "llama-8b",
    name: "Llama 3.1 (8B)",
    path: `${BASE_PATH}/Meta-Llama-3.1-8B-Instruct`, 
    description: "Standard Weights. Fast Chat.",
    vram_estimate: "~16 GB", 
    quantization: undefined // Must be undefined for standard models
  }
];