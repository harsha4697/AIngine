"use client";
import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { ChatArea, Message } from '@/components/ChatArea';
import { api } from '@/utils/api';
import { AVAILABLE_MODELS, ModelConfig } from '@/constants/models';

export default function Home() {
  // --- State ---
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentModel, setCurrentModel] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<string>('offline');
  const [isLocked, setIsLocked] = useState(false);
  
  // Loading States
  const [isSwapping, setIsSwapping] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // --- Initialization & Polling ---
  useEffect(() => {
    const checkStatus = async () => {
      const health = await api.checkHealth();
      setSystemStatus(health.status === 'ok' ? 'online' : 'offline');
      setCurrentModel(health.current_model);
      setIsLocked(health.gpu_locked);
    };

    // Initial check
    checkStatus();

    // Poll every 5 seconds to sync state (e.g. if another tab switches model)
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  // --- Handlers ---

  const handleModelSelect = async (model: ModelConfig) => {
    if (isSwapping || isLocked) return;

    // UI Feedback immediately
    setIsSwapping(true);
    
    // Add system message to chat
    const sysMsg: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: `🔄 System: Unloading ${currentModel || 'previous model'} and initializing ${model.name}... Please wait ~20s.`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, sysMsg]);

    try {
      await api.loadModel(model.id, model.path, model.quantization);
      setCurrentModel(model.id);
      
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `✅ System: ${model.name} is ready.`,
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ Error: Failed to load model. Check server logs.`,
        timestamp: new Date()
      }]);
    } finally {
      setIsSwapping(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    // 1. Add User Message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsGenerating(true);

    try {
      // 2. Call API
      const data = await api.generateText(text);

      // 3. Add AI Response
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        source: data.source,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "⚠️ Error generating response. Ensure model is loaded.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-black">
      <Sidebar 
        currentModel={currentModel}
        isLocked={isLocked} // If locked, user can't switch models
        status={systemStatus}
        isSwapping={isSwapping}
        onSelectModel={handleModelSelect}
      />
      <ChatArea 
        messages={messages}
        isGenerating={isGenerating}
        isModelReady={!!currentModel && !isSwapping}
        onSend={handleSendMessage}
      />
    </div>
  );
}