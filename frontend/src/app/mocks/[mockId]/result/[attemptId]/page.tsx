'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Trophy,
  CheckCircle2,
  XCircle,
  Clock,
  Timer,
  Sparkles,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  AlertCircle,
  Activity,
  Layers
} from 'lucide-react';
import { api } from '@/lib/api';
import { MockAttemptResult } from '@/types';

export default function MockResultPage() {
  const params = useParams();
  const router = useRouter();
  const attemptId = params?.attemptId as string;

  const [result, setResult] = useState<MockAttemptResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    async function fetchResult() {
      try {
        const res = await api.post(`/mocks/attempts/${attemptId}/finish`);
        setResult(res.data);
      } catch (err) {
        console.error('Failed to load mock result:', err);
      } finally {
        setLoading(false);
      }
    }
    if (attemptId) fetchResult();
  }, [attemptId]);

  const handleUpdateStudyPlan = async () => {
    setRegenerating(true);
    try {
      await api.post('/plans/generate');
      router.push('/plan');
    } catch (e) {
      console.error('Failed to regenerate plan:', e);
    } finally {
      setRegenerating(false);
    }
  };

  if (loading || !result) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="flex items-center space-x-3 text-slate-400">
          <Activity className="w-6 h-6 animate-spin text-brand-500" />
          <span className="text-sm font-medium">Synthesizing AI Debrief & Scoring...</span>
        </div>
      </div>
    );
  }

  const debrief = (result.ai_debrief as any) || {};

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Result Hero Header */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-dark-900 via-dark-850 to-dark-900 border border-dark-800 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase text-brand-400">
              <Trophy className="w-4 h-4 text-accent-amber" />
              <span>Examination Debrief & Scorecard</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">{result.mock_title}</h1>
            <p className="text-xs text-slate-300">
              Exam mode completed in {Math.round(result.time_spent_seconds / 60)} minutes.
            </p>
          </div>

          {/* Big Score Counter */}
          <div className="flex items-center space-x-4 bg-dark-950/80 p-4 rounded-2xl border border-dark-700">
            <div className="text-center">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Score</div>
              <div className="text-3xl font-black text-accent-emerald font-mono mt-0.5">
                {result.score} <span className="text-sm text-slate-500 font-normal">/ {result.max_score}</span>
              </div>
            </div>
            <div className="w-px h-10 bg-dark-800" />
            <div className="text-center">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Accuracy</div>
              <div className="text-3xl font-black text-accent-cyan font-mono mt-0.5">
                {Math.round(result.accuracy)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3 Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-dark-900 border border-dark-800">
          <div className="text-xs text-slate-400 font-medium mb-1">Questions Solved</div>
          <div className="text-2xl font-bold text-white font-mono">
            {result.questions_solved} / {result.total_questions}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            {result.questions_attempted} attempted
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-dark-900 border border-dark-800">
          <div className="text-xs text-slate-400 font-medium mb-1">Average Time / Problem</div>
          <div className="text-2xl font-bold text-accent-amber font-mono">
            {Math.round((result.time_management_summary?.avg_per_problem || 0) / 60)} mins
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            Pacing: {result.time_management_summary?.speed_rating || 'Optimal'}
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-dark-900 border border-dark-800">
          <div className="text-xs text-slate-400 font-medium mb-1">Gamification XP Awarded</div>
          <div className="text-2xl font-bold text-brand-400 font-mono">+150 XP</div>
          <div className="text-[11px] text-slate-500 mt-1">Mock simulation milestone earned</div>
        </div>
      </div>

      {/* AI Performance Report Section */}
      <div className="p-8 rounded-3xl bg-dark-900 border border-brand-500/30 shadow-xl space-y-6">
        <div className="flex items-center space-x-2.5">
          <Sparkles className="w-5 h-5 text-accent-cyan" />
          <h2 className="text-lg font-bold text-white">AI Coach Performance Debrief</h2>
        </div>

        <p className="text-sm text-slate-300 leading-relaxed font-sans">
          {debrief.summary || "Your mock test highlights strong fundamental problem solving with opportunity for speed optimization on complex graph and DP problems."}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-dark-800/50 border border-dark-700 space-y-2">
            <span className="text-xs font-bold text-accent-emerald uppercase tracking-wider">Strong Areas</span>
            <ul className="list-disc pl-4 space-y-1 text-xs text-slate-300">
              {debrief.strongAreas?.map((item: string, i: number) => (
                <li key={i}>{item}</li>
              )) || <li>Arrays & Mathematics</li>}
            </ul>
          </div>

          <div className="p-4 rounded-2xl bg-dark-800/50 border border-dark-700 space-y-2">
            <span className="text-xs font-bold text-rose-400 uppercase tracking-wider">Priority Gaps & Time Sinks</span>
            <ul className="list-disc pl-4 space-y-1 text-xs text-slate-300">
              {debrief.weakAreas?.map((item: string, i: number) => (
                <li key={i}>{item}</li>
              )) || <li>Graphs & Dynamic Programming</li>}
            </ul>
          </div>
        </div>

        {/* Action Items */}
        <div className="p-4 rounded-2xl bg-dark-800/30 border border-dark-700 space-y-2">
          <span className="text-xs font-bold text-accent-amber uppercase tracking-wider">Recommended Action Items</span>
          <ul className="list-disc pl-4 space-y-1 text-xs text-slate-300">
            {debrief.actionItems?.map((item: string, i: number) => (
              <li key={i}>{item}</li>
            )) || <li>Practice targeted BFS/DFS grid traversal drills.</li>}
          </ul>
        </div>

        {/* Call to action button */}
        <button
          onClick={handleUpdateStudyPlan}
          disabled={regenerating}
          className="w-full py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-accent-cyan hover:opacity-95 text-white font-bold text-sm shadow-xl flex items-center justify-center space-x-2 transition-all hover:scale-[1.01]"
        >
          <BrainCircuit className="w-4 h-4" />
          <span>{regenerating ? 'Adapting Roadmap...' : 'Adapt My AI Study Plan with these Results'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Problem by Problem Breakdown */}
      <div className="p-6 rounded-3xl bg-dark-900 border border-dark-800 space-y-4">
        <h3 className="text-base font-bold text-white">Problem Breakdown</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-slate-400 border-b border-dark-800">
              <tr>
                <th className="py-3 px-4">Problem</th>
                <th className="py-3 px-4">Difficulty</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Marks</th>
                <th className="py-3 px-4 text-right">Practice</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-800 font-mono">
              {result.problem_breakdown?.map((p, i) => (
                <tr key={i} className="hover:bg-dark-850">
                  <td className="py-3 px-4 font-sans font-semibold text-white">{p.title}</td>
                  <td className="py-3 px-4 text-slate-400">{p.difficulty}</td>
                  <td className="py-3 px-4 font-bold">
                    <span className={p.status === 'ACCEPTED' ? 'text-accent-emerald' : 'text-rose-400'}>
                      {p.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{p.marks_awarded} / {p.marks}</td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      href={`/practice/${p.slug}`}
                      className="px-2.5 py-1 rounded bg-dark-800 hover:bg-dark-700 text-brand-400 text-xs font-sans font-semibold inline-block"
                    >
                      Review
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
