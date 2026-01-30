import axios from 'axios';

// --- CONFIGURATION ---
// 1. Get the raw variable
let rawUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 2. SAFETY CHECK
// If the URL doesn't start with http, force it to use HTTPS
if (!rawUrl.startsWith('http')) {
  rawUrl = `https://${rawUrl}`;
}

// 3. Remove trailing slashes
const API_BASE_URL = rawUrl.replace(/\/$/, "");

console.log("🔌 Connected to Gateway:", API_BASE_URL);

/**
 * HELPER: Get the API Key
 * Priority: 1. localStorage (User Override) 2. Environment Variable (Master)
 */
const getApiKey = () => {
  if (typeof window !== 'undefined') {
    const savedKey = localStorage.getItem('user_api_key');
    if (savedKey) return savedKey;
  }
  return process.env.NEXT_PUBLIC_AI_ENGINE_KEY || '';
};

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
  checkHealth: async (): Promise<HealthResponse> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, {
        headers: { 'api_key': getApiKey() }
      });
      return response.data;
    } catch (error) {
      console.error("Health check failed", error);
      return { status: 'offline', current_model: null, gpu_locked: false };
    }
  },

  // 2. Swap Model (Admin)
  loadModel: async (modelId: string, modelPath: string, quantization?: string) => {
    const response = await axios.post(`${API_BASE_URL}/admin/load-model`, 
      {
        model_id: modelId,
        model_path: modelPath,
        quantization: quantization || null
      },
      {
        headers: { 'api_key': getApiKey() }
      }
    );
    return response.data;
  },

  // 3. Send Chat Prompt
  generateText: async (prompt: string): Promise<GenerateResponse> => {
    const response = await axios.post(`${API_BASE_URL}/generate`, 
      {
        prompt: prompt,
        max_tokens: 200
      },
      {
        headers: { 'api_key': getApiKey() }
      }
    );
    return response.data;
  }
};