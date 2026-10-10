'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import {
  Timer,
  Code2,
  Play,
  Send,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { api } from '@/lib/api';
import { formatTime } from '@/lib/utils';
import { MockStartResponse, MockProblemItem } from '@/types';
import FormattedContent from '@/components/FormattedContent';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

const STARTER_CODES: Record<string, string> = {
  cpp: `#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(NULL);\n    // CodeVita Mock Solution\n    \n    return 0;\n}`,
  python: `import sys\n\ndef solve():\n    lines = sys.stdin.read().split()\n    if not lines:\n        return\n    # CodeVita Mock Solution\n\nif __name__ == '__main__':\n    solve()`,
  java: `import java.util.*;\nimport java.io.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // CodeVita Mock Solution\n    }\n}`,
  c: `#include <stdio.h>\n\nint main() {\n    // CodeVita Mock Solution\n    return 0;\n}`
};

export default function MockExamArenaPage() {
  const params = useParams();
  const router = useRouter();
  const mockId = params?.mockId as string;

  const [mockData, setMockData] = useState<MockStartResponse | null>(null);
  const [currentProblemIdx, setCurrentProblemIdx] = useState(0);
  const [problemDetail, setProblemDetail] = useState<any>(null);
  const [language, setLanguage] = useState('cpp');
  const [codes, setCodes] = useState<Record<string, string>>({});
  const [remainingSeconds, setRemainingSeconds] = useState<number>(0);
  const [isSubmittingProblem, setIsSubmittingProblem] = useState(false);
  const [lastSubmissionStatus, setLastSubmissionStatus] = useState<any>(null);
  const [showFinishModal, setShowFinishModal] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [securityNotice, setSecurityNotice] = useState<string | null>(null);

  const triggerSecurityWarning = () => {
    setSecurityNotice("⚠️ Copy and paste are disabled to preserve competitive programming exam integrity. Please write your code manually.");
    setTimeout(() => setSecurityNotice(null), 4000);
  };

  // Initialize mock attempt
  useEffect(() => {
    async function initMock() {
      try {
        const res = await api.post(`/mocks/${mockId}/start`);
        const data: MockStartResponse = res.data;
        setMockData(data);
        setRemainingSeconds(data.remaining_seconds);

        // Initialize code templates for all problems
        const initCodes: Record<string, string> = {};
        data.problems.forEach(p => {
          initCodes[p.problem_id] = STARTER_CODES['cpp'];
        });
        setCodes(initCodes);

        // Load first problem detail
        if (data.problems.length > 0) {
          loadProblemDetail(data.problems[0].slug);
        }
      } catch (err) {
        console.error('Failed to initialize mock attempt:', err);
      }
    }
    if (mockId) initMock();
  }, [mockId]);

  // Server-authoritative timer countdown
  useEffect(() => {
    if (remainingSeconds <= 0 && mockData) {
      if (mockData.attempt_id) handleFinishExam(true);
      return;
    }

    const timer = setInterval(() => {
      setRemainingSeconds(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          handleFinishExam(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [remainingSeconds, mockData]);

  const loadProblemDetail = async (probSlug: string) => {
    try {
      const res = await api.get(`/problems/${probSlug}`);
      setProblemDetail(res.data);
      setLastSubmissionStatus(null);
    } catch (e) {
      console.error('Error loading problem detail:', e);
    }
  };

  const handleSelectProblem = (idx: number) => {
    if (!mockData) return;
    setCurrentProblemIdx(idx);
    const targetProb = mockData.problems[idx];
    loadProblemDetail(targetProb.slug);
  };

  const handleSubmitProblem = async () => {
    if (!mockData || !problemDetail) return;
    const currentProb = mockData.problems[currentProblemIdx];
    setIsSubmittingProblem(true);
    setLastSubmissionStatus(null);

    try {
      const res = await api.post(`/mocks/attempts/${mockData.attempt_id}/submit`, {
        problem_id: currentProb.problem_id,
        language,
        code: codes[currentProb.problem_id] || ''
      });
      setLastSubmissionStatus(res.data);

      // Update user status on problem in state
      if (res.data.status === 'ACCEPTED') {
        setMockData(prev => {
          if (!prev) return prev;
          const updatedProbs = [...prev.problems];
          updatedProbs[currentProblemIdx].user_status = 'SOLVED';
          return { ...prev, problems: updatedProbs };
        });
      } else {
        setMockData(prev => {
          if (!prev) return prev;
          const updatedProbs = [...prev.problems];
          if (updatedProbs[currentProblemIdx].user_status !== 'SOLVED') {
            updatedProbs[currentProblemIdx].user_status = 'ATTEMPTED';
          }
          return { ...prev, problems: updatedProbs };
        });
      }
    } catch (e) {
      console.error('Mock problem submit error:', e);
    } finally {
      setIsSubmittingProblem(false);
    }
  };

  const handleFinishExam = async (isAutoExpire: boolean = false) => {
    if (!mockData) return;
    setFinishing(true);
    try {
      const res = await api.post(`/mocks/attempts/${mockData.attempt_id}/finish`);
      router.push(`/mocks/${mockId}/result/${mockData.attempt_id}`);
    } catch (e) {
      console.error('Error finishing mock:', e);
    } finally {
      setFinishing(false);
    }
  };

  if (!mockData || !problemDetail) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <div className="flex items-center space-x-3 text-slate-400">
          <Clock className="w-6 h-6 animate-spin text-brand-500" />
          <span className="text-sm font-medium">Loading Examination Chamber...</span>
        </div>
      </div>
    );
  }

  const currentProbMeta = mockData.problems[currentProblemIdx];

  return (
    <div className="h-screen flex flex-col bg-dark-950 overflow-hidden select-none">
      {/* Exam Header */}
      <div className="h-14 px-6 bg-dark-900 border-b border-dark-800 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-4">
          <span className="font-bold text-white text-sm tracking-tight">{mockData.title}</span>
          <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[10px] font-bold">
            <ShieldAlert className="w-3 h-3" />
            <span>AI Assistance Disabled (Exam Mode)</span>
          </div>
        </div>

        {/* Server Authoritative Timer */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 px-4 py-1.5 rounded-xl bg-dark-950 border border-dark-700 font-mono">
            <Timer className="w-4 h-4 text-accent-amber animate-pulse" />
            <span className="text-base font-bold text-white tracking-widest">{formatTime(remainingSeconds)}</span>
          </div>

          <button
            onClick={() => setShowFinishModal(true)}
            className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-colors"
          >
            End & Submit Exam
          </button>
        </div>
      </div>

      {/* Question Palette Navigation Bar */}
      <div className="h-11 px-6 bg-dark-900/50 border-b border-dark-800 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2">
          {mockData.problems.map((p, idx) => {
            const isSelected = currentProblemIdx === idx;
            const isSolved = p.user_status === 'SOLVED';
            const isAttempted = p.user_status === 'ATTEMPTED';
            return (
              <button
                key={p.problem_id}
                onClick={() => handleSelectProblem(idx)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                  isSelected
                    ? 'bg-brand-600 text-white ring-2 ring-brand-400/50'
                    : isSolved
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : isAttempted
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-dark-800 text-slate-400 hover:text-white'
                }`}
              >
                <span>Q{p.order_index}</span>
                {isSolved && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
              </button>
            );
          })}
        </div>

        <div className="flex items-center space-x-4 text-[11px] text-slate-400">
          <span className="flex items-center space-x-1"><div className="w-2 h-2 rounded-full bg-emerald-400" /> <span>Solved</span></span>
          <span className="flex items-center space-x-1"><div className="w-2 h-2 rounded-full bg-amber-400" /> <span>Attempted</span></span>
          <span className="flex items-center space-x-1"><div className="w-2 h-2 rounded-full bg-slate-500" /> <span>Unopened</span></span>
        </div>
      </div>

      {/* Split Arena */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 overflow-hidden">
        {/* Problem Statement */}
        <div className="p-6 overflow-y-auto border-r border-neutral-800 bg-neutral-950 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white tracking-tight">{problemDetail.title}</h2>
            <span className="text-xs font-mono font-bold text-black bg-white px-2 py-0.5 rounded shadow-sm">
              {currentProbMeta.marks} Marks
            </span>
          </div>

          <div>
            <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Statement</h3>
            <FormattedContent content={problemDetail.statement} />
          </div>

          <div>
            <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Input Format</h3>
            <div className="bg-black p-3.5 rounded-xl border border-neutral-800">
              <FormattedContent content={problemDetail.input_format} isMonoBlock />
            </div>
          </div>

          <div>
            <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Output Format</h3>
            <div className="bg-black p-3.5 rounded-xl border border-neutral-800">
              <FormattedContent content={problemDetail.output_format} isMonoBlock />
            </div>
          </div>

          <div>
            <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Constraints</h3>
            <div className="bg-black p-3.5 rounded-xl border border-neutral-800">
              <FormattedContent content={problemDetail.constraints} isMonoBlock />
            </div>
          </div>

          {problemDetail.examples?.map((ex: any, i: number) => (
            <div key={i} className="space-y-2">
              <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider">Example {i + 1}</h3>
              <div className="p-3.5 rounded-xl bg-black border border-neutral-800 space-y-2 text-xs font-mono">
                <div>
                  <span className="text-neutral-500 font-semibold block">Input:</span>
                  <pre className="text-neutral-200 mt-0.5 whitespace-pre-wrap">{ex.input}</pre>
                </div>
                <div>
                  <span className="text-neutral-500 font-semibold block">Output:</span>
                  <pre className="text-white font-bold mt-0.5 whitespace-pre-wrap">{ex.output}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Code Editor & Submissions */}
        <div className="flex flex-col h-full bg-dark-900 overflow-hidden">
          {/* Header */}
          <div className="h-10 px-4 border-b border-dark-800 bg-dark-900 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Code2 className="w-4 h-4 text-brand-400" />
              <select
                value={language}
                onChange={(e) => {
                  setLanguage(e.target.value);
                  setCodes(prev => ({ ...prev, [currentProbMeta.problem_id]: STARTER_CODES[e.target.value] || '' }));
                }}
                className="bg-dark-800 border border-dark-700 text-xs text-white rounded-lg px-2.5 py-1 focus:outline-none focus:border-brand-500"
              >
                <option value="cpp">C++ 17</option>
                <option value="python">Python 3</option>
                <option value="java">Java 21</option>
                <option value="c">C 11</option>
              </select>
            </div>

            <button
              onClick={handleSubmitProblem}
              disabled={isSubmittingProblem}
              className="px-4 py-1 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center space-x-1.5 transition-all shadow-sm"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isSubmittingProblem ? 'Evaluating...' : 'Submit Answer'}</span>
            </button>
          </div>

          {/* Security Notice Banner */}
          {securityNotice && (
            <div className="px-3 py-1.5 bg-neutral-900 border-b border-neutral-700 text-[11px] text-white flex items-center justify-between">
              <span>{securityNotice}</span>
              <button onClick={() => setSecurityNotice(null)} className="text-neutral-400 hover:text-white ml-2 text-xs">✕</button>
            </div>
          )}

          {/* Monaco Editor Container with Copy/Paste Prevention */}
          <div
            className="flex-1 min-h-[300px] relative"
            onPaste={(e) => { e.preventDefault(); triggerSecurityWarning(); }}
            onCopy={(e) => { e.preventDefault(); triggerSecurityWarning(); }}
            onCut={(e) => { e.preventDefault(); triggerSecurityWarning(); }}
            onContextMenu={(e) => { e.preventDefault(); }}
          >
            <MonacoEditor
              height="100%"
              language={language === 'c' || language === 'cpp' ? 'cpp' : language}
              theme="vs-dark"
              value={codes[currentProbMeta.problem_id] || ''}
              onChange={(value) => {
                setCodes(prev => ({ ...prev, [currentProbMeta.problem_id]: value || '' }));
              }}
              onMount={(editor, monaco) => {
                editor.onKeyDown((e: any) => {
                  const isCtrlOrCmd = e.ctrlKey || e.metaKey;
                  if (
                    (isCtrlOrCmd && (e.code === 'KeyV' || e.code === 'KeyC' || e.code === 'KeyX' || e.browserEvent?.key === 'v' || e.browserEvent?.key === 'c' || e.browserEvent?.key === 'x')) ||
                    (e.shiftKey && e.code === 'Insert') ||
                    (e.ctrlKey && e.code === 'Insert')
                  ) {
                    e.preventDefault();
                    e.stopPropagation();
                    triggerSecurityWarning();
                  }
                });
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV, () => {
                  triggerSecurityWarning();
                });
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC, () => {
                  triggerSecurityWarning();
                });
              }}
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                padding: { top: 12 },
                contextmenu: false,
                dragAndDrop: false,
              }}
            />
          </div>

          {/* Mock Console Feedback */}
          <div className="h-36 border-t border-dark-800 bg-dark-950 p-4 font-mono text-xs overflow-y-auto">
            {lastSubmissionStatus ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Submission Outcome:</span>
                  <span className={lastSubmissionStatus.status === 'ACCEPTED' ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                    {lastSubmissionStatus.status}
                  </span>
                </div>
                <div className="text-slate-400">
                  {lastSubmissionStatus.passed_count} / {lastSubmissionStatus.total_count} Test Cases Passed
                  {lastSubmissionStatus.marks_awarded > 0 && ` (${lastSubmissionStatus.marks_awarded} Marks Awarded)`}
                </div>
                {lastSubmissionStatus.compiler_output && (
                  <pre className="text-rose-400 bg-rose-950/20 p-2 rounded border border-rose-500/20 whitespace-pre-wrap">
                    {lastSubmissionStatus.compiler_output}
                  </pre>
                )}
              </div>
            ) : (
              <div className="text-slate-500 italic">
                Submissions in Exam Mode are scored immediately. Hidden test cases remain private.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Finish Exam Confirmation Modal */}
      {showFinishModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="max-w-md w-full p-6 rounded-3xl bg-dark-900 border border-dark-800 shadow-2xl space-y-4 text-center">
            <AlertTriangle className="w-10 h-10 text-accent-amber mx-auto" />
            <h3 className="text-lg font-bold text-white">Finalize & Submit Mock Exam?</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Are you sure you want to end your exam attempt? Your score and comprehensive AI performance report will be generated.
            </p>

            <div className="flex space-x-3 pt-2">
              <button
                onClick={() => setShowFinishModal(false)}
                className="flex-1 py-2.5 rounded-xl bg-dark-800 text-slate-300 hover:text-white text-xs font-semibold"
              >
                Return to Exam
              </button>
              <button
                onClick={() => handleFinishExam(false)}
                disabled={finishing}
                className="flex-1 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold"
              >
                {finishing ? 'Calculating...' : 'Yes, End Exam'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
