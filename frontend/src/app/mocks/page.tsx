'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Clock,
  Timer,
  Play,
  Activity
} from 'lucide-react';
import { api } from '@/lib/api';
import { MockTest } from '@/types';

export default function MockTestsPage() {
  const router = useRouter();
  const [mocks, setMocks] = useState<MockTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [startingId, setStartingId] = useState<string | null>(null);

  useEffect(() => {
    async function fetchMocks() {
      try {
        const res = await api.get('/mocks');
        setMocks(res.data);
      } catch (e) {
        console.error('Error fetching mock tests:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchMocks();
  }, []);

  const handleStartMock = async (mockId: string) => {
    setStartingId(mockId);
    try {
      const res = await api.post(`/mocks/${mockId}/start`);
      router.push(`/mocks/${mockId}/take`);
    } catch (e) {
      console.error('Failed to start mock:', e);
    } finally {
      setStartingId(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* Header */}
      <div className="pb-4 border-b border-neutral-800">
        <h1 className="text-xl font-bold text-white tracking-tight">Mock Examinations</h1>
        <p className="text-xs text-neutral-400 mt-0.5">
          Simulate contest conditions under strict server-authoritative timers.
        </p>
      </div>

      {/* Mocks List */}
      {loading ? (
        <div className="py-16 text-center">
          <Activity className="w-5 h-5 animate-spin text-white mx-auto mb-2" />
          <p className="text-xs text-neutral-500 font-mono">Loading mock exams...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {mocks.map((mock) => (
            <div
              key={mock.id}
              className="p-5 rounded-xl bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-colors flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black border border-neutral-800 text-neutral-300">
                    {mock.mock_type}
                  </span>
                  <span className="text-xs text-neutral-400 font-mono flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-neutral-500" />
                    <span>{mock.duration_minutes} mins</span>
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white">{mock.title}</h3>
                <p className="text-xs text-neutral-400 line-clamp-2">{mock.description}</p>

                <div className="text-[11px] text-neutral-500 font-mono pt-1">
                  <span>{mock.total_questions} Questions • {mock.allowed_languages?.join(', ')}</span>
                </div>
              </div>

              <button
                onClick={() => handleStartMock(mock.id)}
                disabled={startingId === mock.id}
                className="w-full py-2 rounded-lg bg-white hover:bg-neutral-200 disabled:opacity-50 text-black font-semibold text-xs flex items-center justify-center space-x-1.5 transition-all shadow-sm"
              >
                <Play className="w-3 h-3 fill-black text-black" />
                <span>{startingId === mock.id ? 'Starting...' : 'Start Mock Exam'}</span>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
