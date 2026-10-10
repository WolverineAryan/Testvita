'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import {
  Code2,
  Play,
  Send,
  Sparkles,
  BrainCircuit,
  Lightbulb,
  BookOpen,
  CheckCircle2,
  XCircle,
  Clock,
  RotateCcw,
  ArrowLeft,
  X,
  MessageSquare,
  AlertCircle,
  Terminal,
  RefreshCw
} from 'lucide-react';
import { api } from '@/lib/api';
import { getDifficultyColor } from '@/lib/utils';
import { ProblemDetail, TestCaseResult, CodeRunResponse, SubmissionResponse } from '@/types';
import FormattedContent from '@/components/FormattedContent';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

const STARTER_CODES: Record<string, string> = {
  python: `import sys\n\ndef solve():\n    input_data = sys.stdin.read().split()\n    if not input_data:\n        return\n    \n    # Write your solution here\n    # Example: n = int(input_data[0])\n\nif __name__ == '__main__':\n    solve()`,
  cpp: `#include <iostream>\n#include <vector>\n#include <numeric>\n#include <algorithm>\n#include <unordered_map>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(NULL);\n    \n    // Write your solution here\n    \n    return 0;\n}`,
  java: `import java.util.*;\nimport java.io.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Write your solution here\n    }\n}`,
  c: `#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\nint main() {\n    // Write your solution here\n    return 0;\n}`
};

export default function ProblemSolvingPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;

  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [activeTab, setActiveTab] = useState<'statement' | 'hints' | 'editorial'>('statement');
  const [revealedHints, setRevealedHints] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  // Execution states
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [runResult, setRunResult] = useState<CodeRunResponse | null>(null);
  const [submissionResult, setSubmissionResult] = useState<SubmissionResponse | null>(null);

  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewData, setReviewData] = useState<any>(null);
  const [showTutorDrawer, setShowTutorDrawer] = useState(false);
  const [tutorMessage, setTutorMessage] = useState('');
  const [tutorLoading, setTutorLoading] = useState(false);
  const [tutorChat, setTutorChat] = useState<Array<{ sender: 'user' | 'ai'; text: string }>>([
    { sender: 'ai', text: "Hello! I am your CodeVita AI Coach. Ask me about algorithms, time complexity, debugging edge cases, or request a Socratic hint." }
  ]);

  const [securityNotice, setSecurityNotice] = useState<string | null>(null);

  const triggerSecurityWarning = () => {
    setSecurityNotice("⚠️ Copy and paste are disabled to preserve competitive programming exam integrity. Please write your code manually.");
    setTimeout(() => setSecurityNotice(null), 4000);
  };

  useEffect(() => {
    async function fetchProblem() {
      try {
        const res = await api.get(`/problems/${slug}`);
        const p = res.data;
        setProblem(p);
        setCode(STARTER_CODES[language] || STARTER_CODES['python']);
      } catch (err) {
        console.error('Failed to load problem:', err);
      } finally {
        setLoading(false);
      }
    }
    if (slug) fetchProblem();
  }, [slug]);

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    setCode(STARTER_CODES[newLang] || '');
  };

  const handleRun = async () => {
    if (!problem) return;
    setIsRunning(true);
    setRunResult(null);
    setSubmissionResult(null);

    try {
      const res = await api.post('/execution/run', {
        problem_id: problem.id,
        language,
        code
      });
      setRunResult(res.data);
    } catch (err: any) {
      setRunResult({
        status: 'SYSTEM_ERROR',
        total_count: 0,
        passed_count: 0,
        execution_time_ms: 0,
        memory_kb: 0,
        compiler_output: err.response?.data?.detail || 'Execution service unreachable. Please ensure the backend server is running.',
        test_case_results: []
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!problem) return;
    setIsSubmitting(true);
    setSubmissionResult(null);
    setRunResult(null);

    try {
      const res = await api.post('/problems/submit', {
        problem_id: problem.id,
        language,
        code
      });
      setSubmissionResult(res.data);
    } catch (err: any) {
      setSubmissionResult({
        id: 'err',
        user_id: '',
        problem_id: problem.id,
        language,
        code,
        status: 'COMPILATION_ERROR',
        execution_time_ms: 0,
        memory_kb: 0,
        test_cases_passed: 0,
        total_test_cases: 0,
        compiler_output: err.response?.data?.detail || 'Submission evaluation error',
        is_mock: false,
        created_at: new Date().toISOString(),
        test_case_results: []
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAskTutor = async (mode: string = 'TUTOR', customMsg?: string) => {
    const msgToSend = customMsg || tutorMessage;
    if (!msgToSend.trim() || !problem) return;

    setTutorChat(prev => [...prev, { sender: 'user', text: msgToSend }]);
    setTutorMessage('');
    setTutorLoading(true);

    try {
      const res = await api.post('/ai/tutor', {
        problem_id: problem.id,
        language,
        code,
        message: msgToSend,
        mode
      });
      setTutorChat(prev => [...prev, { sender: 'ai', text: res.data.reply }]);
    } catch (err) {
      setTutorChat(prev => [
        ...prev,
        { sender: 'ai', text: "I'm having trouble connecting to the AI Coach API. Please check your network or NVIDIA API key." }
      ]);
    } finally {
      setTutorLoading(false);
    }
  };

  const handleRequestReview = async () => {
    if (!problem) return;
    setShowReviewModal(true);
    setReviewLoading(true);
    setReviewData(null);

    try {
      const res = await api.post('/ai/review', {
        problem_id: problem.id,
        language,
        code
      });
      setReviewData(res.data);
    } catch (err) {
      console.error('Review failed:', err);
    } finally {
      setReviewLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="flex items-center space-x-3 text-neutral-400">
          <Clock className="w-5 h-5 animate-spin text-white" />
          <span className="text-xs font-mono">Loading problem statement and editor workspace...</span>
        </div>
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center space-y-4">
        <p className="text-sm text-neutral-400 font-mono">Problem not found or active session expired.</p>
        <button
          onClick={() => router.push('/practice')}
          className="px-4 py-2 rounded-lg bg-white text-black font-semibold text-xs shadow-sm hover:bg-neutral-200"
        >
          Return to Practice Arena
        </button>
      </div>
    );
  }

  const diffStyle = getDifficultyColor(problem.difficulty);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-black overflow-hidden select-none">
      {/* Top Workspace Action Bar */}
      <div className="h-14 px-4 bg-neutral-950 border-b border-neutral-800 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => router.push('/practice')}
            className="p-1.5 text-neutral-400 hover:text-white rounded-lg hover:bg-neutral-900 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span className="font-bold text-white text-sm truncate max-w-xs sm:max-w-md">{problem.title}</span>
          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${diffStyle.bg} ${diffStyle.text} ${diffStyle.border}`}>
            {problem.difficulty}
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowTutorDrawer(true)}
            className="px-3 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border border-neutral-700 text-xs font-semibold flex items-center space-x-1.5 transition-colors"
          >
            <BrainCircuit className="w-3.5 h-3.5 text-white" />
            <span className="hidden sm:inline">Ask AI Tutor</span>
          </button>

          <button
            onClick={handleRequestReview}
            className="px-3 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border border-neutral-700 text-xs font-semibold flex items-center space-x-1.5 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-white" />
            <span className="hidden sm:inline">AI Review</span>
          </button>

          <button
            onClick={handleRun}
            disabled={isRunning || isSubmitting}
            className="px-4 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white border border-neutral-700 text-xs font-semibold flex items-center space-x-1.5 transition-all"
          >
            <Play className="w-3.5 h-3.5 text-white" />
            <span>{isRunning ? 'Running...' : 'Run'}</span>
          </button>

          <button
            onClick={handleSubmit}
            disabled={isRunning || isSubmitting}
            className="px-4 py-1.5 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center space-x-1.5 shadow-sm transition-all"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSubmitting ? 'Submitting...' : 'Submit'}</span>
          </button>
        </div>
      </div>

      {/* Main Split Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 overflow-hidden">
        {/* Left Column: Formatted Statement / Hints / Editorial */}
        <div className="flex flex-col h-full border-r border-neutral-800 bg-neutral-950 overflow-hidden">
          {/* Tabs Header */}
          <div className="h-10 px-4 border-b border-neutral-800 bg-black flex items-center space-x-4 shrink-0">
            <button
              onClick={() => setActiveTab('statement')}
              className={`text-xs font-semibold py-2.5 border-b-2 transition-colors ${
                activeTab === 'statement'
                  ? 'border-white text-white'
                  : 'border-transparent text-neutral-400 hover:text-white'
              }`}
            >
              Description
            </button>
            <button
              onClick={() => setActiveTab('hints')}
              className={`text-xs font-semibold py-2.5 border-b-2 flex items-center space-x-1 transition-colors ${
                activeTab === 'hints'
                  ? 'border-white text-white'
                  : 'border-transparent text-neutral-400 hover:text-white'
              }`}
            >
              <Lightbulb className="w-3 h-3 text-neutral-300" />
              <span>Hints ({problem.hints?.length || 0})</span>
            </button>
            {problem.editorial && (
              <button
                onClick={() => setActiveTab('editorial')}
                className={`text-xs font-semibold py-2.5 border-b-2 flex items-center space-x-1 transition-colors ${
                  activeTab === 'editorial'
                    ? 'border-white text-white'
                    : 'border-transparent text-neutral-400 hover:text-white'
                }`}
              >
                <BookOpen className="w-3 h-3 text-neutral-300" />
                <span>Editorial</span>
              </button>
            )}
          </div>

          {/* Tab Contents with Formatted LaTeX / Typography */}
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {activeTab === 'statement' && (
              <>
                <div>
                  <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Problem Statement</h3>
                  <FormattedContent content={problem.statement} />
                </div>

                <div>
                  <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Input Format</h3>
                  <div className="bg-black p-3.5 rounded-xl border border-neutral-800">
                    <FormattedContent content={problem.input_format} isMonoBlock />
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Output Format</h3>
                  <div className="bg-black p-3.5 rounded-xl border border-neutral-800">
                    <FormattedContent content={problem.output_format} isMonoBlock />
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-mono font-bold uppercase text-neutral-400 tracking-wider mb-2">Constraints & Limits</h3>
                  <div className="bg-black p-3.5 rounded-xl border border-neutral-800 space-y-2 font-mono">
                    <FormattedContent content={problem.constraints} isMonoBlock />
                    <div className="pt-2 border-t border-neutral-900 text-xs text-neutral-400">
                      Time Limit: {problem.time_limit_seconds}s | Memory Limit: {problem.memory_limit_mb}MB
                    </div>
                  </div>
                </div>

                {problem.examples?.map((ex, i) => (
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
                      {ex.explanation && (
                        <div className="pt-2 border-t border-neutral-900">
                          <FormattedContent content={ex.explanation} className="text-xs italic text-neutral-400" />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </>
            )}

            {activeTab === 'hints' && (
              <div className="space-y-4">
                <p className="text-xs text-neutral-400">
                  Progressive hints designed to guide your algorithmic intuition without giving away the full solution code.
                </p>
                {problem.hints?.map((h, i) => {
                  const isRevealed = revealedHints.includes(i);
                  return (
                    <div key={h.id || i} className="p-4 rounded-xl bg-black border border-neutral-800 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-neutral-200">Hint {i + 1}: {h.title}</span>
                        {!isRevealed ? (
                          <button
                            onClick={() => setRevealedHints(prev => [...prev, i])}
                            className="px-2.5 py-1 rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 border border-neutral-700 text-xs font-semibold transition-colors"
                          >
                            Reveal Hint
                          </button>
                        ) : (
                          <span className="text-[10px] text-white font-mono font-bold uppercase">Revealed</span>
                        )}
                      </div>
                      {isRevealed && (
                        <div className="pt-2 border-t border-neutral-900">
                          <FormattedContent content={h.content} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {activeTab === 'editorial' && (
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-white">Algorithmic Solution & Editorial</h3>
                <div className="p-4 rounded-xl bg-black border border-neutral-800 text-xs text-neutral-300 leading-relaxed">
                  <FormattedContent content={problem.editorial} />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Code Editor & Console Output */}
        <div className="flex flex-col h-full bg-black overflow-hidden">
          {/* Editor Top Bar */}
          <div className="h-10 px-4 border-b border-neutral-800 bg-neutral-950 flex items-center justify-between shrink-0">
            <div className="flex items-center space-x-2">
              <Code2 className="w-4 h-4 text-white" />
              <select
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="bg-black border border-neutral-700 text-xs text-white rounded-lg px-2.5 py-1 focus:outline-none focus:border-white"
              >
                <option value="python">Python 3 (Recommended)</option>
                <option value="cpp">C++ 17 (g++)</option>
                <option value="java">Java 21</option>
                <option value="c">C 11</option>
              </select>
            </div>

            <button
              onClick={() => setCode(STARTER_CODES[language] || '')}
              title="Reset code template"
              className="p-1 text-neutral-400 hover:text-white rounded hover:bg-neutral-900"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Security Notice Banner */}
          {securityNotice && (
            <div className="px-4 py-2 bg-neutral-900 border-b border-neutral-700 text-[11px] text-white flex items-center justify-between animate-fadeIn">
              <span>{securityNotice}</span>
              <button onClick={() => setSecurityNotice(null)} className="text-neutral-400 hover:text-white ml-2">
                <X className="w-3 h-3" />
              </button>
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
              value={code}
              onChange={(value) => setCode(value || '')}
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

          {/* Bottom Console / Submission Evaluation Output */}
          <div className="h-52 border-t border-neutral-800 bg-neutral-950 p-4 overflow-y-auto font-mono text-xs">
            {submissionResult ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {submissionResult.status === 'ACCEPTED' ? (
                      <CheckCircle2 className="w-5 h-5 text-white" />
                    ) : (
                      <XCircle className="w-5 h-5 text-neutral-400" />
                    )}
                    <span className={`font-bold text-sm ${submissionResult.status === 'ACCEPTED' ? 'text-white' : 'text-neutral-300'}`}>
                      {submissionResult.status}
                    </span>
                  </div>
                  <span className="text-neutral-400 text-xs">
                    {submissionResult.test_cases_passed} / {submissionResult.total_test_cases} Test Cases Passed
                  </span>
                </div>

                {submissionResult.compiler_output && (
                  <div className="p-3 rounded-xl bg-black border border-neutral-800 space-y-2 text-neutral-300">
                    <pre className="whitespace-pre-wrap">{submissionResult.compiler_output}</pre>
                    {submissionResult.compiler_output.toLowerCase().includes('missing') && (
                      <button
                        onClick={() => handleLanguageChange('python')}
                        className="px-3 py-1.5 rounded-lg bg-white text-black font-bold text-xs hover:bg-neutral-200 transition-all flex items-center space-x-1.5"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        <span>Switch to Python 3 & Retry</span>
                      </button>
                    )}
                  </div>
                )}

                {submissionResult.status === 'ACCEPTED' && (
                  <div className="p-3 rounded-xl bg-neutral-900 border border-neutral-700 text-white font-sans flex items-center justify-between">
                    <span>Problem Solved! Skill rating & streak updated.</span>
                    <button
                      onClick={handleRequestReview}
                      className="px-3 py-1 rounded bg-white text-black font-semibold text-xs"
                    >
                      Analyze Time Complexity
                    </button>
                  </div>
                )}
              </div>
            ) : runResult ? (
              <div className="space-y-2.5">
                <div className="flex items-center justify-between text-neutral-400 text-xs mb-2">
                  <span>RUN EVALUATION RESULTS</span>
                  <span className={runResult.status === 'SUCCESS' ? 'text-white font-bold' : 'text-neutral-300 font-bold'}>
                    {runResult.status} ({runResult.passed_count}/{runResult.total_count} Passed)
                  </span>
                </div>

                {runResult.compiler_output && (
                  <div className="p-3 rounded-xl bg-black border border-neutral-800 space-y-2 text-neutral-300">
                    <pre className="whitespace-pre-wrap">{runResult.compiler_output}</pre>
                    {runResult.compiler_output.toLowerCase().includes('missing') && (
                      <button
                        onClick={() => handleLanguageChange('python')}
                        className="px-3 py-1.5 rounded-lg bg-white text-black font-bold text-xs hover:bg-neutral-200 transition-all flex items-center space-x-1.5"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        <span>Switch to Python 3 & Retry</span>
                      </button>
                    )}
                  </div>
                )}

                {runResult.test_case_results?.map((tc, i) => (
                  <div key={i} className="p-2.5 rounded bg-black border border-neutral-800 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-neutral-300">Public Test Case {tc.order_index}</span>
                      <span className={tc.status === 'PASSED' ? 'text-white font-bold' : 'text-neutral-400 font-bold'}>
                        {tc.status} ({tc.execution_time_ms}ms)
                      </span>
                    </div>
                    {tc.status !== 'PASSED' && (
                      <div className="text-[11px] text-neutral-400 space-y-0.5">
                        <div>Expected: <span className="text-white">{tc.expected_output}</span></div>
                        <div>Output: <span className="text-neutral-300">{tc.actual_output}</span></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-neutral-500 italic flex items-center space-x-2 pt-2 font-mono">
                <Terminal className="w-4 h-4 text-neutral-600" />
                <span>Console idle. Click &apos;Run&apos; to test against public test cases or &apos;Submit&apos; for official grading.</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Code Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="max-w-2xl w-full p-6 rounded-2xl bg-neutral-950 border border-neutral-800 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-4">
              <div className="flex items-center space-x-2.5">
                <Sparkles className="w-5 h-5 text-white" />
                <h3 className="font-bold text-white text-base">AI Algorithmic Code Review</h3>
              </div>
              <button onClick={() => setShowReviewModal(false)} className="text-neutral-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {reviewLoading ? (
              <div className="py-12 text-center space-y-2">
                <Sparkles className="w-8 h-8 animate-spin text-white mx-auto" />
                <p className="text-xs text-neutral-400 font-mono">Analyzing asymptotic complexities & edge case handling...</p>
              </div>
            ) : reviewData ? (
              <div className="space-y-4 text-xs text-neutral-300">
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-3 rounded-xl bg-black border border-neutral-800">
                    <div className="text-neutral-400 text-[10px] font-mono">Time Complexity</div>
                    <div className="text-sm font-bold text-white font-mono mt-0.5">{reviewData.time_complexity}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-black border border-neutral-800">
                    <div className="text-neutral-400 text-[10px] font-mono">Optimal Target</div>
                    <div className="text-sm font-bold text-white font-mono mt-0.5">{reviewData.optimal_time_complexity}</div>
                  </div>
                  <div className="p-3 rounded-xl bg-black border border-neutral-800">
                    <div className="text-neutral-400 text-[10px] font-mono">Quality Score</div>
                    <div className="text-sm font-bold text-white font-mono mt-0.5">{reviewData.code_quality_score} / 10</div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-black border border-neutral-800 space-y-2">
                  <h4 className="font-bold text-white uppercase text-[11px] font-mono">Correctness & Architecture</h4>
                  <p className="leading-relaxed">{reviewData.correctness_assessment}</p>
                </div>

                {reviewData.strengths && reviewData.strengths.length > 0 && (
                  <div className="p-4 rounded-xl bg-black border border-neutral-800 space-y-2">
                    <h4 className="font-bold text-white uppercase text-[11px] font-mono">Strengths</h4>
                    <ul className="list-disc list-inside space-y-1 text-neutral-300">
                      {reviewData.strengths.map((s: string, i: number) => (
                        <li key={i}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {reviewData.areas_for_optimization && reviewData.areas_for_optimization.length > 0 && (
                  <div className="p-4 rounded-xl bg-black border border-neutral-800 space-y-2">
                    <h4 className="font-bold text-white uppercase text-[11px] font-mono">Optimization Opportunities</h4>
                    <ul className="list-disc list-inside space-y-1 text-neutral-300">
                      {reviewData.areas_for_optimization.map((o: string, i: number) => (
                        <li key={i}>{o}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* Socratic AI Tutor Drawer */}
      {showTutorDrawer && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-neutral-950 border-l border-neutral-800 shadow-2xl flex flex-col">
          <div className="h-14 px-4 border-b border-neutral-800 flex items-center justify-between shrink-0">
            <div className="flex items-center space-x-2">
              <BrainCircuit className="w-5 h-5 text-white" />
              <h3 className="font-bold text-white text-sm">Socratic AI Coach</h3>
            </div>
            <button onClick={() => setShowTutorDrawer(false)} className="text-neutral-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-3 font-sans">
            {tutorChat.map((msg, i) => (
              <div
                key={i}
                className={`p-3.5 rounded-xl text-xs leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-neutral-900 border border-neutral-700 text-white ml-6'
                    : 'bg-black border border-neutral-800 text-neutral-300 mr-6'
                }`}
              >
                <FormattedContent content={msg.text} />
              </div>
            ))}
            {tutorLoading && (
              <div className="p-3 rounded-xl bg-black border border-neutral-800 text-neutral-400 text-xs flex items-center space-x-2 font-mono">
                <BrainCircuit className="w-4 h-4 animate-spin text-white" />
                <span>Formulating Socratic guidance...</span>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-neutral-800 bg-black space-y-2">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Ask about state transitions, time limits, or edge cases..."
                value={tutorMessage}
                onChange={(e) => setTutorMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAskTutor('TUTOR')}
                className="flex-1 bg-neutral-950 border border-neutral-700 rounded-lg px-3 py-2 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-white"
              />
              <button
                onClick={() => handleAskTutor('TUTOR')}
                disabled={tutorLoading || !tutorMessage.trim()}
                className="px-3.5 py-2 rounded-lg bg-white text-black font-semibold text-xs hover:bg-neutral-200 transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
