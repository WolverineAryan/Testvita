'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  CheckCircle2,
  Circle,
  Clock,
  Activity,
  ArrowRight,
  BookOpen,
  Award,
  Sparkles,
  Zap
} from 'lucide-react';
import { api } from '@/lib/api';

export default function TodayFocusPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [activeDay, setActiveDay] = useState<number>(1);
  const [totalDays, setTotalDays] = useState<number>(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchToday();
  }, []);

  async function fetchToday() {
    setLoading(true);
    try {
      const res = await api.get('/plans/active');
      const plan = res.data;
      if (plan && plan.tasks) {
        const targetDay = plan.current_unlocked_day || 1;
        setActiveDay(targetDay);

        const days = Math.max(...plan.tasks.map((t: any) => t.day_number || 1));
        setTotalDays(days);

        const currentDayTasks = plan.tasks.filter((t: any) => t.day_number === targetDay);
        setTasks(currentDayTasks.length > 0 ? currentDayTasks : plan.tasks.slice(0, 4));
      }
    } catch (e) {
      console.error('Error loading today focus:', e);
    } finally {
      setLoading(false);
    }
  }

  const handleToggle = async (taskId: string) => {
    try {
      const res = await api.post(`/plans/tasks/${taskId}/toggle`);
      setTasks(prev =>
        prev.map(t => (t.id === taskId ? { ...t, is_completed: res.data.is_completed } : t))
      );
    } catch (e) {
      console.error('Error toggling task:', e);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex items-center space-x-2 text-neutral-400">
          <Activity className="w-4 h-4 animate-spin text-white" />
          <span className="text-xs font-mono">Loading today&apos;s sprints...</span>
        </div>
      </div>
    );
  }

  const completedCount = tasks.filter(t => t.is_completed).length;
  const totalCount = tasks.length;
  const progressPct = Math.round((completedCount / Math.max(1, totalCount)) * 100);
  const isDayDone = totalCount > 0 && completedCount === totalCount;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-neutral-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Today&apos;s Focus — Day {activeDay}</h1>
            <span className="px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-[10px] font-mono text-neutral-300 font-semibold flex items-center space-x-1">
              <Zap className="w-3 h-3 text-white" />
              <span>Day {activeDay} of {totalDays}</span>
            </span>
          </div>
          <p className="text-xs text-neutral-400 mt-1">
            Sequential training module. Complete all tasks below to unlock Day {Math.min(activeDay + 1, totalDays)}.
          </p>
        </div>

        <div className="flex items-center space-x-3 sm:text-right">
          <Link
            href="/plan"
            className="px-3 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white border border-neutral-800 text-xs font-medium transition-colors"
          >
            Full Roadmap
          </Link>
          <div>
            <span className="text-xs font-mono font-bold text-white">{completedCount}/{totalCount} Done</span>
            <div className="text-[10px] text-neutral-500 font-mono">{progressPct}% completed</div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 w-full bg-neutral-900 rounded-full overflow-hidden">
        <div
          className="h-full bg-white rounded-full transition-all duration-300"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Day Done Celebration */}
      {isDayDone && (
        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-neutral-900 border border-neutral-700 flex items-center justify-center text-white shrink-0">
              <Award className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white">Day {activeDay} Sprints Completed!</h4>
              <p className="text-[11px] text-neutral-400">
                {activeDay < totalDays
                  ? `Day ${activeDay + 1} has been unlocked.`
                  : 'Congratulations! You have completed the entire curriculum.'}
              </p>
            </div>
          </div>

          <Link
            href="/plan"
            className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-neutral-200 text-black font-bold text-xs flex items-center space-x-1.5 transition-all shrink-0 shadow-sm"
          >
            <span>View Roadmap</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Tasks List */}
      <div className="space-y-2.5">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`p-4 rounded-xl border flex items-center justify-between gap-3 transition-colors ${
              task.is_completed
                ? 'bg-neutral-950/60 border-neutral-900 opacity-60'
                : 'bg-neutral-950 border-neutral-800 hover:border-neutral-700'
            }`}
          >
            <div className="flex items-center space-x-3 min-w-0">
              <button
                onClick={() => handleToggle(task.id)}
                className="text-neutral-500 hover:text-white transition-colors shrink-0"
              >
                {task.is_completed ? (
                  <CheckCircle2 className="w-5 h-5 text-white" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
              </button>

              <div className="min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-neutral-900 text-neutral-300 border border-neutral-800 font-semibold">
                    {task.task_type}
                  </span>
                  <h3 className={`text-xs font-bold truncate ${task.is_completed ? 'line-through text-neutral-500' : 'text-white'}`}>
                    {task.title}
                  </h3>
                </div>
                {task.description && (
                  <p className="text-[11px] text-neutral-400 mt-0.5 truncate">{task.description}</p>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-2 shrink-0 pl-3">
              <span className="text-[11px] text-neutral-400 font-mono flex items-center space-x-1">
                <Clock className="w-3 h-3 text-neutral-500" />
                <span>{task.duration_minutes}m</span>
              </span>

              {task.target_problem_slug && (
                <Link
                  href={`/practice/${task.target_problem_slug}`}
                  className="px-3 py-1 rounded bg-white hover:bg-neutral-200 text-black font-semibold text-xs transition-all shadow-sm"
                >
                  Solve
                </Link>
              )}
            </div>
          </div>
        ))}

        {tasks.length === 0 && (
          <div className="py-12 text-center text-xs text-neutral-500 font-mono border border-dashed border-neutral-800 rounded-xl">
            No scheduled tasks for today.
          </div>
        )}
      </div>
    </div>
  );
}
