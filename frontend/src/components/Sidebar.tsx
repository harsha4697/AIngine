"use client";
import React from 'react';
import { Server, Zap, HardDrive, Cpu, Activity, Key, Eye, EyeOff } from 'lucide-react';
import { AVAILABLE_MODELS, ModelConfig } from '@/constants/models';
import { useState, useEffect } from 'react';

interface SidebarProps {
  currentModel: string | null;
  isLocked: boolean;
  status: string; // 'online' | 'offline'
  onSelectModel: (model: ModelConfig) => void;
  isSwapping: boolean; // True when API call is in progress
}

export function Sidebar({ 
  currentModel, 
  isLocked, 
  status, 
  onSelectModel,
  isSwapping 
}: SidebarProps) {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);

  // Load key from localStorage on mount
  useEffect(() => {
    const savedKey = localStorage.getItem('user_api_key');
    if (savedKey) setApiKey(savedKey);
  }, []);

  // Save key to localStorage
  const handleKeyChange = (value: string) => {
    setApiKey(value);
    localStorage.setItem('user_api_key', value);
  };

  return (
    <aside className="w-80 h-screen bg-slate-950 border-r border-slate-800 flex flex-col text-slate-200 shadow-2xl">
      {/* --- Header --- */}
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent flex items-center gap-2">
          <Cpu className="w-6 h-6 text-blue-400" />
          AIngine <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full border border-slate-700">v1.0</span>
        </h1>
        
        {/* Status Indicator */}
        <div className="mt-4 flex items-center gap-3 text-sm font-medium p-3 bg-slate-900/50 rounded-lg border border-slate-800 backdrop-blur-sm">
          <div className="relative">
             <div className={`w-3 h-3 rounded-full ${status === 'online' ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`} />
             {status === 'online' && <div className="absolute inset-0 w-3 h-3 rounded-full bg-emerald-500 blur-sm" />}
          </div>
          <div className="flex flex-col">
            <span className={status === 'online' ? 'text-emerald-400' : 'text-red-400'}>
              {status === 'online' ? 'System Online' : 'System Offline'}
            </span>
            <span className="text-xs text-slate-500 flex items-center gap-1">
              {isLocked ? (
                <span className="text-amber-400 flex items-center gap-1">
                  <Activity className="w-3 h-3" /> GPU Busy
                </span>
              ) : (
                <span className="text-slate-400">GPU Idle</span>
              )}
            </span>
          </div>
        </div>
      </div>

      {/* --- Model Selector --- */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">
          Available Models
        </h2>
        
        {AVAILABLE_MODELS.map((model) => {
          const isActive = currentModel === model.id;
          return (
            <button
              key={model.id}
              onClick={() => !isSwapping && onSelectModel(model)}
              disabled={isSwapping || isActive}
              className={`w-full text-left p-4 rounded-xl border transition-all duration-300 group relative overflow-hidden
                ${isActive 
                  ? 'bg-blue-900/20 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.15)]' 
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-600 hover:bg-slate-800/60'
                }
                ${isSwapping ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <div className="flex justify-between items-start mb-1">
                <span className={`font-semibold ${isActive ? 'text-blue-400' : 'text-slate-300 group-hover:text-white'}`}>
                  {model.name}
                </span>
                {isActive && <Zap className="w-4 h-4 text-blue-400 fill-blue-400/20" />}
              </div>
              
              <p className="text-xs text-slate-500 mb-3">{model.description}</p>
              
              <div className="flex items-center gap-2 text-[10px] text-slate-600 font-mono bg-slate-950/30 p-1.5 rounded-lg w-fit">
                <HardDrive className="w-3 h-3" />
                {model.vram_estimate}
              </div>

              {/* Loading Overlay */}
              {isSwapping && isActive && (
                 <div className="absolute inset-0 bg-slate-950/80 flex items-center justify-center backdrop-blur-sm">
                    <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                 </div>
              )}
            </button>
          );
        })}
      </div>

      {/* --- API Key Settings --- */}
      <div className="p-4 mx-4 mb-4 bg-slate-900/60 border border-slate-800 rounded-xl">
        <div className="flex items-center justify-between mb-2 px-1">
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
            <Key className="w-3 h-3" /> Authentication
          </label>
          <button 
            onClick={() => setShowKey(!showKey)}
            className="text-slate-500 hover:text-slate-300 transition-colors"
          >
            {showKey ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
          </button>
        </div>
        <input 
          type={showKey ? "text" : "password"}
          value={apiKey}
          onChange={(e) => handleKeyChange(e.target.value)}
          placeholder="Enter API Key..."
          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-blue-400 placeholder:text-slate-700 focus:outline-none focus:border-blue-500/50 transition-all font-mono"
        />
        <p className="text-[9px] text-slate-600 mt-2 px-1 leading-relaxed">
          Custom keys override the default session.
        </p>
      </div>

      {/* --- Footer --- */}
      <div className="p-4 border-t border-slate-800 text-[10px] text-slate-600 text-center bg-slate-950/50">
        Powered by vLLM & pgvector
      </div>
    </aside>
  );
}