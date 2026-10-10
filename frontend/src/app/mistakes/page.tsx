'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Activity
} from 'lucide-react';
import { api } from '@/lib/api';

export default function MistakesPage() {
  const [mistakes, setMistakes] = useState<any[]>([]);
  const [filterCategory, setFilterCategory] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMistakes() {
      try {
        const res = await api.get('/analytics/mistakes');
        setMistakes(res.data);
      } catch (e) {
        console.error('Error fetching mistakes:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchMistakes();
  }, []);

  const handleResolve = async (id: string) => {
    try {
      await api.post(`/analytics/mistakes/${id}/resolve`);
      setMistakes(prev =>
        prev.map(m => (m.id === id ? { ...m, is_resolved: true } : m))
      );
    } catch (e) {
      console.error('Error resolving mistake:', e);
    }
  };

  const filteredMistakes = filterCategory
    ? mistakes.filter(m => m.category === filterCategory)
    : mistakes;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-neutral-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Mistakes Notebook</h1>
          <p className="text-xs text-neutral-400 mt-0.5">
            Auto-recorded errors and incorrect submissions.
          </p>
        </div>

        {/* Filter Categories */}
        <div className="flex items-center space-x-1 bg-neutral-900 p-1 rounded-lg border border-neutral-800 text-xs">
          {['', 'LOGIC', 'COMPLEXITY', 'SYNTAX'].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-2.5 py-1 rounded font-semibold transition-all ${
                filterCategory === cat
                  ? 'bg-white text-black'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              {cat || 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Mistake Items */}
      {loading ? (
        <div className="py-16 text-center">
          <Activity className="w-5 h-5 animate-spin text-white mx-auto mb-2" />
          <p className="text-xs text-neutral-500 font-mono">Loading error notebook...</p>
        </div>
      ) : filteredMistakes.length === 0 ? (
        <div className="py-12 text-center bg-neutral-950 rounded-xl border border-neutral-800 p-6">
          <CheckCircle2 className="w-6 h-6 text-white mx-auto mb-2" />
          <h3 className="text-xs font-bold text-white mb-0.5">No Mistakes Logged</h3>
          <p className="text-[11px] text-neutral-500">All submissions passing cleanly.</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {filteredMistakes.map((m) => (
            <div
              key={m.id}
              className={`p-3.5 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition-colors ${
                m.is_resolved
                  ? 'bg-neutral-950/50 border-neutral-900 opacity-60'
                  : 'bg-neutral-950 border-neutral-800 hover:border-neutral-700'
              }`}
            >
              <div className="space-y-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-neutral-900 text-neutral-300 border border-neutral-800">
                    {m.failure_type}
                  </span>
                  <h3 className="text-xs font-bold text-white truncate">{m.problem_title}</h3>
                </div>

                <p className="text-[11px] text-neutral-400 line-clamp-1">
                  {m.ai_insight || `Submission failed on ${m.problem_title}.`}
                </p>
              </div>

              <div className="flex items-center space-x-2 shrink-0">
                {!m.is_resolved ? (
                  <button
                    onClick={() => handleResolve(m.id)}
                    className="px-2.5 py-1 rounded bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white border border-neutral-800 text-xs font-semibold"
                  >
                    Resolve
                  </button>
                ) : (
                  <span className="text-[11px] text-neutral-400 font-mono">Resolved</span>
                )}

                {m.problem_slug && (
                  <Link
                    href={`/practice/${m.problem_slug}`}
                    className="px-2.5 py-1 rounded bg-white hover:bg-neutral-200 text-black font-semibold text-xs transition-all"
                  >
                    Retry
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
