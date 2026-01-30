import axios from 'axios';

// --- CONFIGURATION ---
// In Vercel, this will be your Railway URL (e.g. https://aingine-gateway.up.railway.app)
// In Local Dev, this falls back to localhost:8000
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// --- TYPES ---
export interface HealthResponse {
  status: string;
  current_model: string | null;
  gpu_locked: boolean;
}

export interface GenerateResponse {
  response: string;
  model_used: string;
  source: 'cache ⚡' | 'gpu 🐢';
}

export interface LoadModelRequest {
  model_id: string;
  model_path: string;
  quantization?: string;
}

// --- API FUNCTIONS ---

export const api = {
  // 1. Check System Health
  // The Gateway proxies this request to your home worker to see if it's alive.
  checkHealth: async (): Promise<HealthResponse> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      // If Railway is down or Tunnel is broken, we show offline
      console.error("Health check failed", error);
      return { status: 'offline', current_model: null, gpu_locked: false };
    }
  },

  // 2. Swap Model
  // Admin action sent to the Gateway
  loadModel: async (modelId: string, modelPath: string, quantization?: string) => {
    const response = await axios.post(`${API_BASE_URL}/admin/load-model`, {
      model_id: modelId,
      model_path: modelPath,
      quantization: quantization || null // Send null for standard weights (like Llama)
    });
    return response.data;
  },

  // 3. Send Chat Prompt
  // Vercel -> Railway (Adds Secret) -> ngrok -> Home GPU
  generateText: async (prompt: string): Promise<GenerateResponse> => {
    const response = await axios.post(`${API_BASE_URL}/generate`, {
      prompt: prompt,
      max_tokens: 200
    });
    return response.data;
  }
};