'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Clock,
  RotateCcw,
  CheckCircle2,
  Activity
} from 'lucide-react';
import { api } from '@/lib/api';
import { getDifficultyColor } from '@/lib/utils';

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchReviews() {
      try {
        const res = await api.get('/analytics/reviews');
        setReviews(res.data);
      } catch (e) {
        console.error('Error fetching reviews:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchReviews();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-5">
      {/* Header */}
      <div className="pb-3 border-b border-neutral-800">
        <h1 className="text-xl font-bold text-white tracking-tight">Review Queue</h1>
        <p className="text-xs text-neutral-400 mt-0.5">
          Spaced repetition queue for algorithmic retention.
        </p>
      </div>

      {/* Reviews List */}
      {loading ? (
        <div className="py-16 text-center">
          <Activity className="w-5 h-5 animate-spin text-white mx-auto mb-2" />
          <p className="text-xs text-neutral-500 font-mono">Loading review queue...</p>
        </div>
      ) : reviews.length === 0 ? (
        <div className="py-12 text-center bg-neutral-950 rounded-xl border border-neutral-800 p-6">
          <CheckCircle2 className="w-6 h-6 text-white mx-auto mb-2" />
          <h3 className="text-xs font-bold text-white mb-0.5">No Reviews Due</h3>
          <p className="text-[11px] text-neutral-500">Your review queue is clear.</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {reviews.map((r) => {
            const diffStyle = getDifficultyColor(r.difficulty);
            return (
              <div
                key={r.id}
                className="p-3.5 rounded-xl bg-neutral-950 border border-neutral-800 flex items-center justify-between gap-3 hover:border-neutral-700 transition-colors"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${diffStyle.bg} ${diffStyle.text} ${diffStyle.border}`}>
                      {r.difficulty}
                    </span>
                    <h3 className="text-xs font-bold text-white truncate">{r.problem_title}</h3>
                  </div>

                  <div className="flex items-center space-x-2 text-[11px] text-neutral-500 font-mono">
                    <span>Interval: {r.interval_days}d</span>
                    <span>•</span>
                    <span>Rep #{r.repetitions}</span>
                    <span>•</span>
                    <span className={r.is_due ? 'text-white font-bold' : 'text-neutral-500'}>
                      {r.is_due ? 'Due Today' : `Next: ${new Date(r.next_review_at).toLocaleDateString()}`}
                    </span>
                  </div>
                </div>

                <Link
                  href={`/practice/${r.problem_slug}`}
                  className="px-3 py-1.5 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center space-x-1 transition-all shrink-0 shadow-sm"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Review</span>
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
