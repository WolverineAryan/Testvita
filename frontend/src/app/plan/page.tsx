'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  CheckCircle2,
  Circle,
  Clock,
  Target,
  Activity,
  BookOpen,
  Code2,
  AlertTriangle,
  ArrowRight,
  X,
  Sparkles,
  Zap,
  Check,
  FileDown,
  Lock,
  Unlock,
  ChevronRight,
  Award
} from 'lucide-react';
import { api } from '@/lib/api';
import { StudyPlan, StudyTask } from '@/types';
import FormattedContent from '@/components/FormattedContent';
import { generateRoadmapPDF } from '@/lib/pdfGenerator';

export default function StudyPlanPage() {
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState<StudyTask | null>(null);
  const [copiedCode, setCopiedCode] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [userName, setUserName] = useState<string>('Candidate');
  const [selectedDay, setSelectedDay] = useState<number>(1);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    fetchPlan();
    try {
      const stored = localStorage.getItem('user');
      if (stored) {
        const u = JSON.parse(stored);
        if (u.full_name) setUserName(u.full_name);
      }
    } catch {}
  }, []);

  const fetchPlan = async () => {
    setLoading(true);
    try {
      const res = await api.get('/plans/active');
      const planData: StudyPlan = res.data;
      setPlan(planData);
      if (planData.current_unlocked_day) {
        setSelectedDay(planData.current_unlocked_day);
      }
    } catch (e) {
      console.error('Failed to load study plan:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!plan) return;
    setIsExporting(true);
    try {
      generateRoadmapPDF(plan, userName);
    } catch (err) {
      console.error('Failed to generate PDF:', err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleToggleTask = async (taskId: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setErrorMsg(null);
    try {
      const res = await api.post(`/plans/tasks/${taskId}/toggle`);
      setPlan(prev => {
        if (!prev) return prev;
        const updatedTasks = prev.tasks.map(t =>
          t.id === taskId ? { ...t, is_completed: res.data.is_completed } : t
        );
        const completedCount = updatedTasks.filter(t => t.is_completed).length;
        const pct = Math.round((completedCount / Math.max(1, updatedTasks.length)) * 100);

        // Recompute current unlocked day
        const dayMap: Record<number, StudyTask[]> = {};
        updatedTasks.forEach(t => {
          if (!dayMap[t.day_number]) dayMap[t.day_number] = [];
          dayMap[t.day_number].push(t);
        });
        const dayNums = Object.keys(dayMap).map(Number).sort((a, b) => a - b);
        let unlockedDay = 1;
        for (const d of dayNums) {
          const isDone = dayMap[d].every(t => t.is_completed);
          if (!isDone) {
            unlockedDay = d;
            break;
          }
          unlockedDay = Math.min(d + 1, Math.max(...dayNums));
        }

        return {
          ...prev,
          tasks: updatedTasks,
          completion_percentage: pct,
          current_unlocked_day: unlockedDay
        };
      });

      if (selectedTask && selectedTask.id === taskId) {
        setSelectedTask(prev => prev ? { ...prev, is_completed: res.data.is_completed } : null);
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail || 'Failed to update task.';
      setErrorMsg(detail);
      setTimeout(() => setErrorMsg(null), 4000);
    }
  };

  const handleCopyCode = (codeText: string) => {
    navigator.clipboard.writeText(codeText);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  if (loading || !plan) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex items-center space-x-2 text-neutral-400">
          <Activity className="w-4 h-4 animate-spin text-white" />
          <span className="text-xs font-mono">Loading adaptive study plan & curriculum...</span>
        </div>
      </div>
    );
  }

  // Group tasks by day number
  const tasksByDay: Record<number, StudyTask[]> = {};
  plan.tasks?.forEach(t => {
    if (!tasksByDay[t.day_number]) tasksByDay[t.day_number] = [];
    tasksByDay[t.day_number].push(t);
  });

  const dayNumbers = Object.keys(tasksByDay).map(Number).sort((a, b) => a - b);
  const totalDays = dayNumbers.length ? Math.max(...dayNumbers) : 7;
  const currentUnlockedDay = plan.current_unlocked_day || 1;

  // Active day calculations
  const activeDayTasks = tasksByDay[selectedDay] || [];
  const isSelectedDayLocked = selectedDay > currentUnlockedDay;
  const isSelectedDayCompleted = activeDayTasks.length > 0 && activeDayTasks.every(t => t.is_completed);
  const activeDayCompletedCount = activeDayTasks.filter(t => t.is_completed).length;
  const activeDayTotalCount = activeDayTasks.length;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">{plan.title || 'Adaptive Roadmap'}</h1>
            <span className="flex items-center space-x-1 px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-[10px] font-mono text-neutral-300 font-semibold">
              <Zap className="w-3 h-3 text-white" />
              <span>{totalDays}-Day Progressive Roadmap</span>
            </span>
          </div>
          <p className="text-xs text-neutral-400 mt-1 max-w-xl leading-relaxed">
            {plan.summary || `Complete daily modules sequentially to unlock downstream topics. Adapts live with your practice solves.`}
          </p>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={handleDownloadPDF}
            disabled={isExporting}
            className="px-3.5 py-2 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center space-x-2 transition-all shadow-sm"
          >
            <FileDown className="w-4 h-4" />
            <span>{isExporting ? 'Generating PDF...' : `Download ${totalDays}-Day PDF Syllabus`}</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-3 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-xs flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Progress & Priority Topics Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Progress Card */}
        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-neutral-400 font-medium">Curriculum Progress</span>
            <span className="font-bold text-white font-mono">{plan.completion_percentage || 0}%</span>
          </div>
          <div className="h-1.5 w-full bg-neutral-900 rounded-full overflow-hidden">
            <div
              className="h-full bg-white rounded-full transition-all duration-300"
              style={{ width: `${plan.completion_percentage || 0}%` }}
            />
          </div>
          <p className="text-[10px] text-neutral-500 font-mono">
            {plan.tasks?.filter(t => t.is_completed).length} / {plan.tasks?.length} tasks completed • Day {currentUnlockedDay} Active
          </p>
        </div>

        {/* Priority Topics */}
        <div className="sm:col-span-2 p-4 rounded-xl bg-neutral-950 border border-neutral-800 space-y-2">
          <div className="flex items-center space-x-1.5 text-xs font-bold text-neutral-300">
            <Target className="w-3.5 h-3.5 text-white" />
            <span>Target Mastery Focus</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {plan.priority_topics?.slice(0, 6).map((pt, i) => (
              <span key={i} className="text-[10px] font-mono px-2.5 py-1 rounded bg-black border border-neutral-800 text-neutral-300 flex items-center space-x-1">
                <span className="text-white font-bold">{pt.topic}</span>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Progressive Day Navigation Tabs */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-neutral-400 uppercase font-mono tracking-wider">
            Sequential Learning Track
          </span>
          <span className="text-[11px] text-neutral-500 font-mono">
            Active: Day {currentUnlockedDay} of {totalDays}
          </span>
        </div>

        <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
          {dayNumbers.map((d) => {
            const dTasks = tasksByDay[d] || [];
            const isCompleted = dTasks.length > 0 && dTasks.every(t => t.is_completed);
            const isUnlocked = d <= currentUnlockedDay;
            const isCurrent = (selectedDay === d);

            return (
              <button
                key={d}
                onClick={() => setSelectedDay(d)}
                className={`px-3.5 py-2 rounded-xl text-xs font-mono transition-all flex items-center space-x-2 shrink-0 border ${
                  isCurrent
                    ? 'bg-white text-black font-bold border-white shadow-sm'
                    : isCompleted
                    ? 'bg-neutral-900 text-neutral-300 border-neutral-800 hover:border-neutral-700'
                    : isUnlocked
                    ? 'bg-neutral-950 text-white border-neutral-700 hover:border-neutral-600'
                    : 'bg-neutral-950/50 text-neutral-600 border-neutral-900 cursor-not-allowed'
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : isUnlocked ? (
                  <Unlock className={`w-3.5 h-3.5 ${isCurrent ? 'text-black' : 'text-white'}`} />
                ) : (
                  <Lock className="w-3.5 h-3.5 text-neutral-600" />
                )}
                <span>Day {d}</span>
                {isCompleted && <span className="text-[9px] opacity-75">(Done)</span>}
              </button>
            );
          })}
        </div>
      </div>

      {/* Single Day View Container */}
      <div className="p-5 rounded-2xl bg-neutral-950 border border-neutral-800 space-y-4 shadow-sm">
        {/* Day Header & Status */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-neutral-800">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-white tracking-tight">Day {selectedDay} Curriculum</h2>
              {isSelectedDayLocked ? (
                <span className="px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-[10px] font-mono text-neutral-500 flex items-center space-x-1">
                  <Lock className="w-3 h-3" />
                  <span>Locked</span>
                </span>
              ) : isSelectedDayCompleted ? (
                <span className="px-2 py-0.5 rounded bg-neutral-900 border border-neutral-700 text-[10px] font-mono text-emerald-400 flex items-center space-x-1 font-semibold">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Day Completed</span>
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded bg-white text-black text-[10px] font-mono font-bold flex items-center space-x-1">
                  <Sparkles className="w-3 h-3" />
                  <span>In Progress</span>
                </span>
              )}
            </div>
            <p className="text-xs text-neutral-400 mt-0.5">
              {isSelectedDayLocked
                ? `Complete all Day ${selectedDay - 1} tasks to unlock this stage.`
                : `${activeDayTasks.reduce((acc, t) => acc + t.duration_minutes, 0)} mins total training scheduled`}
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs font-mono font-bold text-white">
              {activeDayCompletedCount}/{activeDayTotalCount} Tasks Done
            </span>
            <div className="text-[10px] text-neutral-500 font-mono">
              {Math.round((activeDayCompletedCount / Math.max(1, activeDayTotalCount)) * 100)}% of Day {selectedDay}
            </div>
          </div>
        </div>

        {/* Day Locked Banner */}
        {isSelectedDayLocked ? (
          <div className="py-12 px-6 rounded-xl bg-black border border-neutral-800 text-center space-y-3">
            <div className="w-10 h-10 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center mx-auto text-neutral-500">
              <Lock className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-white">Day {selectedDay} is Locked</h3>
              <p className="text-xs text-neutral-400 max-w-md mx-auto leading-relaxed">
                To maintain mastery invariants, complete all tasks in <strong className="text-white">Day {currentUnlockedDay}</strong> first. Once finished, Day {currentUnlockedDay + 1} unlocks automatically.
              </p>
            </div>
            <button
              onClick={() => setSelectedDay(currentUnlockedDay)}
              className="px-4 py-2 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs transition-all inline-flex items-center space-x-1.5 shadow-sm"
            >
              <span>Go to Active Day {currentUnlockedDay}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <>
            {/* Completion Celebration & Advance Banner */}
            {isSelectedDayCompleted && selectedDay < totalDays && (
              <div className="p-4 rounded-xl bg-neutral-900 border border-neutral-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-black border border-neutral-700 flex items-center justify-center text-white shrink-0">
                    <Award className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Day {selectedDay} Completed!</h4>
                    <p className="text-[11px] text-neutral-400">Day {selectedDay + 1} is now unlocked and ready.</p>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedDay(selectedDay + 1)}
                  className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-neutral-200 text-black font-bold text-xs flex items-center space-x-1 transition-all shrink-0 shadow-sm"
                >
                  <span>Proceed to Day {selectedDay + 1}</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* Tasks List for Selected Day */}
            <div className="space-y-2.5">
              {activeDayTasks.map(t => (
                <div
                  key={t.id}
                  onClick={() => setSelectedTask(t)}
                  className={`p-3.5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs transition-all cursor-pointer ${
                    t.is_completed
                      ? 'bg-black border-neutral-900 opacity-60'
                      : 'bg-black border-neutral-800 hover:border-neutral-700'
                  }`}
                >
                  <div className="flex items-start sm:items-center space-x-3 min-w-0">
                    <button
                      onClick={(e) => handleToggleTask(t.id, e)}
                      className="text-neutral-500 hover:text-white shrink-0 mt-0.5 sm:mt-0"
                    >
                      {t.is_completed ? (
                        <CheckCircle2 className="w-4 h-4 text-white" />
                      ) : (
                        <Circle className="w-4 h-4" />
                      )}
                    </button>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-neutral-900 text-neutral-300 border border-neutral-800 shrink-0 font-semibold">
                      {t.task_type}
                    </span>
                    <div className="min-w-0">
                      <div className={`font-semibold truncate ${t.is_completed ? 'line-through text-neutral-500' : 'text-white'}`}>
                        {t.title}
                      </div>
                      {t.description && (
                        <div className="text-[11px] text-neutral-400 truncate max-w-md">
                          {t.description}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 shrink-0 self-end sm:self-auto">
                    <span className="text-[11px] text-neutral-500 font-mono flex items-center space-x-1">
                      <Clock className="w-3 h-3 text-neutral-600" />
                      <span>{t.duration_minutes}m</span>
                    </span>

                    <button
                      onClick={() => setSelectedTask(t)}
                      className="px-2.5 py-1 rounded bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white border border-neutral-800 text-[11px] font-medium transition-colors flex items-center space-x-1"
                    >
                      <BookOpen className="w-3 h-3" />
                      <span>Guide</span>
                    </button>

                    {t.target_problem_slug ? (
                      <Link
                        href={`/practice/${t.target_problem_slug}`}
                        onClick={(e) => e.stopPropagation()}
                        className="px-3 py-1 rounded bg-white hover:bg-neutral-200 text-black font-bold text-[11px] transition-all flex items-center space-x-1 shadow-sm"
                      >
                        <span>Solve</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    ) : (
                      <Link
                        href={`/practice?topic=${encodeURIComponent(t.topic_name || '')}`}
                        onClick={(e) => e.stopPropagation()}
                        className="px-3 py-1 rounded bg-neutral-900 hover:bg-neutral-800 text-white font-medium text-[11px] border border-neutral-700 transition-all flex items-center space-x-1 shadow-sm"
                      >
                        <span>Practice</span>
                        <ArrowRight className="w-3 h-3 text-neutral-400" />
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Interactive Concept & Learning Resource Modal */}
      {selectedTask && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="max-w-2xl w-full p-6 rounded-2xl bg-neutral-950 border border-neutral-800 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-neutral-800 pb-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-neutral-900 text-white border border-neutral-800 font-bold uppercase">
                    {selectedTask.task_type}
                  </span>
                  <span className="text-xs font-mono text-neutral-400">Day {selectedTask.day_number} • {selectedTask.duration_minutes} Minutes</span>
                </div>
                <h3 className="font-bold text-white text-base mt-1.5">{selectedTask.title}</h3>
                {selectedTask.description && (
                  <p className="text-xs text-neutral-400 mt-0.5">{selectedTask.description}</p>
                )}
              </div>
              <button
                onClick={() => setSelectedTask(null)}
                className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-neutral-900 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Resource Details */}
            {selectedTask.resource ? (
              <div className="space-y-4 text-xs text-neutral-300">
                {/* Asymptotic Bounds Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-black border border-neutral-800">
                    <div className="text-neutral-400 text-[10px] font-mono">Target Time Complexity</div>
                    <div className="text-xs font-bold text-white font-mono mt-1">{selectedTask.resource.time_complexity}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-black border border-neutral-800">
                    <div className="text-neutral-400 text-[10px] font-mono">Space Bounds</div>
                    <div className="text-xs font-bold text-white font-mono mt-1">{selectedTask.resource.space_complexity}</div>
                  </div>
                </div>

                {/* Theoretical Overview */}
                <div className="p-4 rounded-xl bg-black border border-neutral-800 space-y-2">
                  <div className="flex items-center space-x-2">
                    <BookOpen className="w-4 h-4 text-white" />
                    <h4 className="font-bold text-white uppercase text-[11px] font-mono">Concept & Algorithmic Foundation</h4>
                  </div>
                  <FormattedContent content={selectedTask.resource.overview} className="leading-relaxed text-neutral-300" />
                </div>

                {/* Key Invariants */}
                {selectedTask.resource.key_invariants && selectedTask.resource.key_invariants.length > 0 && (
                  <div className="p-4 rounded-xl bg-black border border-neutral-800 space-y-2">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4 text-white" />
                      <h4 className="font-bold text-white uppercase text-[11px] font-mono">Core Invariants & Rules</h4>
                    </div>
                    <ul className="space-y-1.5 pl-1">
                      {selectedTask.resource.key_invariants.map((inv: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-2 text-neutral-300">
                          <span className="text-white shrink-0 font-bold">•</span>
                          <span>{inv}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Code Template */}
                {selectedTask.resource.code_template && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Code2 className="w-4 h-4 text-white" />
                        <h4 className="font-bold text-white uppercase text-[11px] font-mono">Standard Template & Implementation</h4>
                      </div>
                      <button
                        onClick={() => handleCopyCode(selectedTask.resource?.code_template || '')}
                        className="px-2.5 py-1 rounded bg-neutral-900 hover:bg-neutral-800 text-[10px] font-mono text-neutral-300 border border-neutral-800 transition-colors flex items-center space-x-1"
                      >
                        {copiedCode ? <Check className="w-3 h-3 text-white" /> : null}
                        <span>{copiedCode ? 'Copied' : 'Copy Code'}</span>
                      </button>
                    </div>
                    <div className="rounded-xl bg-black border border-neutral-800 p-3.5 font-mono text-[11px] overflow-x-auto text-neutral-200 leading-relaxed whitespace-pre">
                      {selectedTask.resource.code_template}
                    </div>
                  </div>
                )}

                {/* Pitfalls & Edge Cases */}
                {selectedTask.resource.pitfalls && selectedTask.resource.pitfalls.length > 0 && (
                  <div className="p-4 rounded-xl bg-black border border-neutral-800 space-y-2">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="w-4 h-4 text-white" />
                      <h4 className="font-bold text-white uppercase text-[11px] font-mono">CodeVita Traps & Edge Cases</h4>
                    </div>
                    <ul className="space-y-1.5 pl-1">
                      {selectedTask.resource.pitfalls.map((pit: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-2 text-neutral-300">
                          <span className="text-neutral-500 shrink-0">⚠</span>
                          <span>{pit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-black border border-neutral-800 text-xs text-neutral-400">
                Resource guide calibrated for {selectedTask.title}.
              </div>
            )}

            {/* Action Footer */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-neutral-800">
              <button
                onClick={() => handleToggleTask(selectedTask.id)}
                className="px-3.5 py-2 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white border border-neutral-700 text-xs font-semibold flex items-center space-x-2 transition-colors"
              >
                {selectedTask.is_completed ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-white" />
                    <span>Mark as Incomplete</span>
                  </>
                ) : (
                  <>
                    <Circle className="w-4 h-4 text-neutral-400" />
                    <span>Mark as Completed</span>
                  </>
                )}
              </button>

              <div className="flex items-center space-x-2">
                <Link
                  href={`/practice?topic=${encodeURIComponent(selectedTask.topic_name || selectedTask.resource?.title || '')}`}
                  className="px-3.5 py-2 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white border border-neutral-700 text-xs font-semibold flex items-center space-x-1.5 transition-colors"
                >
                  <span>Browse {selectedTask.topic_name || 'Topic'} Problems</span>
                  <ArrowRight className="w-3.5 h-3.5 text-neutral-400" />
                </Link>

                {selectedTask.target_problem_slug && (
                  <Link
                    href={`/practice/${selectedTask.target_problem_slug}`}
                    className="px-4 py-2 rounded-lg bg-white hover:bg-neutral-200 text-black font-bold text-xs transition-all flex items-center space-x-1.5 shadow-sm"
                  >
                    <span>Solve Challenge</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
