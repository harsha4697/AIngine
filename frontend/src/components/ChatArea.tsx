"use client";
import React, { useRef, useEffect, useState } from 'react';
import { Send, Cpu, Zap, User, Bot } from 'lucide-react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  source?: 'cache ⚡' | 'gpu 🐢'; // Only for assistant
  timestamp: Date;
}

interface ChatAreaProps {
  messages: Message[];
  isGenerating: boolean;
  onSend: (text: string) => void;
  isModelReady: boolean;
}

export function ChatArea({ messages, isGenerating, onSend, isModelReady }: ChatAreaProps) {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isGenerating]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating || !isModelReady) return;
    onSend(input);
    setInput('');
  };

  return (
    <main className="flex-1 flex flex-col bg-slate-950 relative overflow-hidden">
      {/* Background Decor (Subtle Glows) */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-20%] left-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px]" />
      </div>

      {/* --- Message List --- */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent z-10">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-600 opacity-50">
            <Bot className="w-16 h-16 mb-4 text-slate-700" />
            <p>Select a model and say hello.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[80%] flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 
                ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-emerald-600 text-white'}`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>

              {/* Bubble */}
              <div className={`relative p-4 rounded-2xl shadow-lg border backdrop-blur-md
                ${msg.role === 'user' 
                  ? 'bg-blue-600/20 border-blue-500/30 text-slate-100 rounded-tr-none' 
                  : 'bg-slate-900/60 border-slate-800 text-slate-200 rounded-tl-none'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                
                {/* Meta Data (Source & Time) */}
                <div className="mt-2 flex items-center justify-end gap-2 text-[10px] opacity-60">
                  <span>{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  {msg.source && (
                    <span className={`px-1.5 py-0.5 rounded border flex items-center gap-1
                      ${msg.source.includes('cache') 
                        ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' 
                        : 'bg-purple-500/10 border-purple-500/30 text-purple-400'
                      }`}>
                      {msg.source.includes('cache') ? <Zap size={10} /> : <Cpu size={10} />}
                      {msg.source.toUpperCase()}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Loading State */}
        {isGenerating && (
          <div className="flex justify-start w-full">
            <div className="flex gap-3 max-w-[80%]">
              <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center flex-shrink-0 animate-pulse">
                <Bot size={16} className="text-white" />
              </div>
              <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl rounded-tl-none flex items-center gap-2">
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* --- Input Area --- */}
      <div className="p-6 bg-slate-950 border-t border-slate-800 z-20">
        <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isModelReady ? "Ask anything..." : "Load a model to start..."}
            disabled={!isModelReady || isGenerating}
            className="w-full bg-slate-900/50 border border-slate-800 text-slate-200 rounded-xl pl-5 pr-12 py-4 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-slate-600"
          />
          <button
            type="submit"
            disabled={!isModelReady || isGenerating || !input.trim()}
            className="absolute right-2 top-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors disabled:opacity-0 disabled:pointer-events-none"
          >
            <Send size={18} />
          </button>
        </form>
        <div className="text-center mt-2 text-[10px] text-slate-600">
           AIngine v1.0 • Running on Local Hardware • Inputs are Cached
        </div>
      </div>
    </main>
  );
}