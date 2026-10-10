'use client';

import React, { useState } from 'react';
import {
  BrainCircuit,
  Send,
  Sparkles,
  Bug,
  Lightbulb,
  BookOpen,
  Activity
} from 'lucide-react';
import FormattedContent from '@/components/FormattedContent';
import { api } from '@/lib/api';

const MODES = [
  { id: 'TUTOR', label: 'Coach', icon: BrainCircuit },
  { id: 'DEBUG', label: 'Debugger', icon: Bug },
  { id: 'HINT', label: 'Hints', icon: Lightbulb },
  { id: 'EXPLAIN', label: 'Complexity', icon: BookOpen }
];

export default function AITutorPage() {
  const [selectedMode, setSelectedMode] = useState('TUTOR');
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState<Array<{ sender: 'user' | 'ai'; text: string }>>([
    {
      sender: 'ai',
      text: "Hello! I am your AI Competitive Programming Coach. Ask me about dynamic programming states, time complexity, graph traversals, or debugging edge cases."
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (customPrompt?: string) => {
    const textToSend = customPrompt || message;
    if (!textToSend.trim()) return;

    const newChat = [...chat, { sender: 'user' as const, text: textToSend }];
    setChat(newChat);
    setMessage('');
    setLoading(true);

    try {
      const res = await api.post('/ai/tutor', {
        mode: selectedMode,
        message: textToSend,
        language: 'cpp'
      });
      setChat([...newChat, { sender: 'ai' as const, text: res.data.reply }]);
    } catch (e) {
      setChat([...newChat, { sender: 'ai' as const, text: 'Unable to reach AI Coach. Please check your connection and try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-neutral-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">AI Coach</h1>
          <p className="text-xs text-neutral-400 mt-0.5">
            Socratic guidance and algorithmic analysis.
          </p>
        </div>

        {/* Mode Selector */}
        <div className="flex items-center space-x-1 bg-neutral-900 p-1 rounded-lg border border-neutral-800">
          {MODES.map((m) => {
            const Icon = m.icon;
            const isSelected = selectedMode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setSelectedMode(m.id)}
                className={`px-2.5 py-1 rounded text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                  isSelected
                    ? 'bg-white text-black'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                <Icon className="w-3 h-3" />
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Chat Stream */}
      <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 flex flex-col h-[520px]">
        <div className="flex-1 overflow-y-auto space-y-3 pr-2">
          {chat.map((c, i) => (
            <div
              key={i}
              className={`flex flex-col ${c.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-2xl p-3.5 rounded-xl text-xs leading-relaxed ${
                  c.sender === 'user'
                    ? 'bg-white text-black font-medium'
                    : 'bg-neutral-900 border border-neutral-800 text-neutral-200 w-full'
                }`}
              >
                {c.sender === 'user' ? (
                  c.text
                ) : (
                  <FormattedContent content={c.text} />
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-2 text-xs text-neutral-400 p-2.5 rounded-lg bg-neutral-900 border border-neutral-800 w-fit">
              <Sparkles className="w-3.5 h-3.5 animate-spin text-white" />
              <span>Thinking...</span>
            </div>
          )}
        </div>

        {/* Quick Prompts */}
        <div className="pt-2.5 border-t border-neutral-800 flex flex-wrap gap-1.5">
          {[
            "Formulate 2D DP state transitions",
            "Dijkstra vs 0-1 BFS",
            "Why is my solution getting TLE?",
            "Binary search on answer edge cases"
          ].map((promptText, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(promptText)}
              className="px-2 py-0.5 rounded bg-neutral-900 hover:bg-neutral-800 text-[10px] text-neutral-400 hover:text-white border border-neutral-800 transition-colors"
            >
              {promptText}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="pt-2.5 flex items-center space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask AI Coach a question..."
            className="flex-1 px-3 py-2 rounded-lg bg-black border border-neutral-800 text-xs text-white placeholder:text-neutral-600 focus:outline-none focus:border-neutral-500"
          />

          <button
            onClick={() => handleSend()}
            disabled={loading || !message.trim()}
            className="p-2 rounded-lg bg-white hover:bg-neutral-200 disabled:opacity-50 text-black transition-all shrink-0"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
