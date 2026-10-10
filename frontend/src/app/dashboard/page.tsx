'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Trophy,
  Flame,
  Clock,
  Target,
  ArrowRight,
  BrainCircuit,
  AlertCircle,
  CheckCircle2,
  BookOpen,
  Activity,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { api } from '@/lib/api';
import { getDifficultyColor } from '@/lib/utils';

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [skillMatrix, setSkillMatrix] = useState<any>(null);
  const [activePlan, setActivePlan] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const [dashRes, skillRes, planRes, recRes] = await Promise.allSettled([
          api.get('/analytics/dashboard'),
          api.get('/skills/matrix'),
          api.get('/plans/active'),
          api.get('/recommendations?limit=4')
        ]);

        if (dashRes.status === 'fulfilled') setDashboardData(dashRes.value.data);
        if (skillRes.status === 'fulfilled') setSkillMatrix(skillRes.value.data);
        if (planRes.status === 'fulfilled') setActivePlan(planRes.value.data);
        if (recRes.status === 'fulfilled') setRecommendations(recRes.value.data);
      } catch (e) {
        console.error('Error loading dashboard:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex items-center space-x-2 text-neutral-400">
          <Activity className="w-4 h-4 animate-spin text-white" />
          <span className="text-xs font-mono">Loading dashboard...</span>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  const user = dashboardData?.user || {};
  const todayTasks = activePlan?.tasks?.filter((t: any) => t.day_number === 1) || [];
  const isUncalibrated = (stats.total_attempted || 0) === 0;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* Calibration Banner */}
      {isUncalibrated && (
        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <Target className="w-4 h-4 text-white shrink-0" />
            <div>
              <h3 className="text-xs font-bold text-white">Diagnostic Scan Recommended</h3>
              <p className="text-[11px] text-neutral-400">
                Calibrate your baseline topic ratings and unlock your personalized roadmap.
              </p>
            </div>
          </div>
          <Link
            href="/diagnostic"
            className="px-3 py-1.5 rounded-lg bg-white hover:bg-neutral-200 text-black text-xs font-semibold shrink-0 transition-all flex items-center space-x-1"
          >
            <span>Start Test</span>
            <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
      )}

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-neutral-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Dashboard
          </h1>
          <p className="text-xs text-neutral-400 mt-0.5">
            {user.full_name || 'Candidate'} • {user.target_competition || 'TCS CodeVita'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/today"
            className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center space-x-1.5 transition-all shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-black" />
            <span>Today&apos;s Focus</span>
          </Link>
          <Link
            href="/mocks"
            className="px-3.5 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border border-neutral-800 text-xs font-semibold flex items-center space-x-1.5 transition-all"
          >
            <Clock className="w-3.5 h-3.5 text-white" />
            <span>Mocks</span>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 mb-1">
            <span className="text-xs font-medium">Skill Rating</span>
            <Target className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="text-xl font-bold text-white font-mono">
            {isUncalibrated ? '0%' : `${stats.overall_score || 0}%`}
          </div>
          <div className="text-[10px] text-neutral-500 font-mono mt-0.5">
            {isUncalibrated ? 'Uncalibrated' : 'Weighted score'}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 mb-1">
            <span className="text-xs font-medium">Problems Solved</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{stats.problems_solved || 0}</div>
          <div className="text-[10px] text-neutral-500 font-mono mt-0.5">{stats.accuracy_percentage || 0}% Accuracy</div>
        </div>

        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 mb-1">
            <span className="text-xs font-medium">Streak</span>
            <Flame className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{stats.current_streak || 0} Days</div>
          <div className="text-[10px] text-neutral-500 font-mono mt-0.5">Best: {stats.longest_streak || 0}d</div>
        </div>

        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800">
          <div className="flex items-center justify-between text-neutral-400 mb-1">
            <span className="text-xs font-medium">Mocks Completed</span>
            <Trophy className="w-3.5 h-3.5 text-white" />
          </div>
          <div className="text-xl font-bold text-white font-mono">{stats.mocks_completed || 0}</div>
          <div className="text-[10px] text-neutral-500 font-mono mt-0.5">Score: {stats.best_mock_score || 0}</div>
        </div>
      </div>

      {/* Main Grid: Today's Tasks & Topic Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Tasks */}
          <div className="p-5 rounded-xl bg-neutral-950 border border-neutral-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-white">Today&apos;s Sprints</h3>
              <Link href="/today" className="text-xs text-neutral-400 hover:text-white flex items-center space-x-1 transition-colors">
                <span>View All</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {todayTasks.length > 0 ? (
              <div className="space-y-2">
                {todayTasks.map((t: any) => (
                  <div
                    key={t.id}
                    className="p-3 rounded-lg bg-black border border-neutral-800 flex items-center justify-between hover:border-neutral-700 transition-colors"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center space-x-2">
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-neutral-900 text-neutral-300 border border-neutral-800">
                          {t.task_type}
                        </span>
                        <span className="text-xs font-bold text-white">{t.title}</span>
                      </div>
                      <p className="text-[11px] text-neutral-400 line-clamp-1">{t.description}</p>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0 pl-3">
                      <span className="text-[11px] text-neutral-400 font-mono">{t.duration_minutes}m</span>
                      {t.target_problem_slug && (
                        <Link
                          href={`/practice/${t.target_problem_slug}`}
                          className="px-2.5 py-1 rounded bg-white hover:bg-neutral-200 text-black font-semibold text-xs transition-all"
                        >
                          Solve
                        </Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-4 text-center text-xs text-neutral-500 font-mono border border-dashed border-neutral-800 rounded-lg">
                No active tasks for today.
              </div>
            )}
          </div>

          {/* Topic Mastery Grid */}
          <div className="p-5 rounded-xl bg-neutral-950 border border-neutral-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-white">Topic Mastery</h3>
              <span className="text-xs text-neutral-500 font-mono">{skillMatrix?.topic_scores?.length || 0} Topics</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {skillMatrix?.topic_scores?.map((topic: any) => {
                const score = Math.round(topic.score || 0);
                const hasAttempted = (topic.problems_attempted || 0) > 0;
                return (
                  <div key={topic.topic_id} className="p-3 rounded-lg bg-black border border-neutral-800/80 space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-neutral-200">{topic.topic_name}</span>
                      <span className={`font-mono text-xs ${hasAttempted ? 'text-white font-bold' : 'text-neutral-500'}`}>
                        {hasAttempted ? `${score}%` : 'Unassessed'}
                      </span>
                    </div>

                    <div className="h-1 w-full rounded-full bg-neutral-900 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-white transition-all duration-300"
                        style={{ width: `${hasAttempted ? Math.max(5, score) : 0}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-neutral-500 font-mono">
                      <span>{topic.problems_solved || 0}/{topic.problems_attempted || 0} solved</span>
                      <span>Conf: {hasAttempted ? `${Math.round((topic.confidence || 0) * 100)}%` : '0%'}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Recommendations & Retention */}
        <div className="space-y-6">
          {/* Recommended Problems */}
          <div className="p-5 rounded-xl bg-neutral-950 border border-neutral-800 space-y-3">
            <div className="flex items-center space-x-2">
              <BrainCircuit className="w-3.5 h-3.5 text-white" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-white">Recommended</h3>
            </div>

            <div className="space-y-2">
              {recommendations.map((prob) => {
                const diffStyle = getDifficultyColor(prob.difficulty);
                return (
                  <Link
                    key={prob.id}
                    href={`/practice/${prob.slug}`}
                    className="block p-3 rounded-lg bg-black border border-neutral-800/80 hover:border-neutral-600 transition-colors group"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${diffStyle.bg} ${diffStyle.text} ${diffStyle.border}`}>
                        {prob.difficulty}
                      </span>
                      <span className="text-[10px] text-neutral-500 font-mono">~{prob.estimated_time_minutes}m</span>
                    </div>

                    <h4 className="text-xs font-bold text-white group-hover:text-neutral-300 transition-colors line-clamp-1">
                      {prob.title}
                    </h4>

                    {prob.recommendation_reason && (
                      <p className="text-[10px] text-neutral-400 mt-1 line-clamp-1">
                        {prob.recommendation_reason}
                      </p>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Mistakes & Review Queue */}
          <div className="p-5 rounded-xl bg-neutral-950 border border-neutral-800 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">Retention Hub</h3>

            <div className="grid grid-cols-2 gap-2.5">
              <Link
                href="/mistakes"
                className="p-3 rounded-lg bg-black border border-neutral-800 hover:border-neutral-600 text-left transition-colors"
              >
                <div className="flex items-center space-x-1.5 text-xs text-neutral-300 mb-1">
                  <AlertCircle className="w-3 h-3 text-white" />
                  <span>Mistakes</span>
                </div>
                <div className="text-lg font-bold text-white font-mono">{stats.mistakes_logged || 0}</div>
              </Link>

              <Link
                href="/reviews"
                className="p-3 rounded-lg bg-black border border-neutral-800 hover:border-neutral-600 text-left transition-colors"
              >
                <div className="flex items-center space-x-1.5 text-xs text-neutral-300 mb-1">
                  <BookOpen className="w-3 h-3 text-white" />
                  <span>Reviews</span>
                </div>
                <div className="text-lg font-bold text-white font-mono">{stats.pending_reviews || 0}</div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
