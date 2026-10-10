'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import {
  Activity,
  Code2,
  Play,
  Send,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import { api } from '@/lib/api';
import FormattedContent from '@/components/FormattedContent';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

const STARTER_CODES: Record<string, string> = {
  cpp: `#include <iostream>\n#include <vector>\n#include <numeric>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(NULL);\n    \n    // Write your solution here\n    \n    return 0;\n}`,
  python: `import sys\n\ndef solve():\n    lines = sys.stdin.read().split()\n    if not lines:\n        return\n    # Write your solution here\n\nif __name__ == '__main__':\n    solve()`,
  java: `import java.util.*;\nimport java.io.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // Write your solution here\n    }\n}`,
  c: `#include <stdio.h>\n\nint main() {\n    // Write your solution here\n    return 0;\n}`
};

export default function DiagnosticPage() {
  const router = useRouter();
  const [problems, setProblems] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [language, setLanguage] = useState('python');
  const [codes, setCodes] = useState<Record<string, string>>({});
  const [timeSpent, setTimeSpent] = useState<Record<string, number>>({});
  const [isRunning, setIsRunning] = useState(false);
  const [runResult, setRunResult] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);
  const [diagnosticResult, setDiagnosticResult] = useState<any>(null);
  const [securityNotice, setSecurityNotice] = useState<string | null>(null);

  const triggerSecurityWarning = () => {
    setSecurityNotice("⚠️ Copy and paste are disabled to preserve competitive programming exam integrity. Please write your code manually.");
    setTimeout(() => setSecurityNotice(null), 4000);
  };

  useEffect(() => {
    async function loadProblems() {
      try {
        const res = await api.get('/skills/diagnostic/problems');
        const probList = res.data;
        setProblems(probList);

        const initialCodes: Record<string, string> = {};
        const initialTimes: Record<string, number> = {};
        probList.forEach((p: any) => {
          initialCodes[p.id] = STARTER_CODES[language] || STARTER_CODES['python'];
          initialTimes[p.id] = 0;
        });
        setCodes(initialCodes);
        setTimeSpent(initialTimes);
      } catch (e) {
        console.error('Failed to load diagnostic problems:', e);
      }
    }
    loadProblems();
  }, []);

  const currentProblem = problems[currentIndex];

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    if (currentProblem) {
      setCodes(prev => ({
        ...prev,
        [currentProblem.id]: STARTER_CODES[newLang] || ''
      }));
    }
  };

  const handleRun = async () => {
    if (!currentProblem) return;
    setIsRunning(true);
    setRunResult(null);

    try {
      const res = await api.post('/execution/run', {
        problem_id: currentProblem.id,
        language,
        code: codes[currentProblem.id] || ''
      });
      setRunResult(res.data);
    } catch (err: any) {
      setRunResult({
        status: 'SYSTEM_ERROR',
        compiler_output: err.response?.data?.detail || 'Execution error'
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmitDiagnostic = async () => {
    setSubmitting(true);
    try {
      const payload = {
        answers: problems.map(p => ({
          problem_id: p.id,
          language,
          code: codes[p.id] || '',
          time_spent_seconds: timeSpent[p.id] || 300,
          hints_used: 0
        }))
      };

      const res = await api.post('/skills/diagnostic/submit', payload);
      setDiagnosticResult(res.data);
    } catch (err) {
      console.error('Error submitting diagnostic:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (diagnosticResult) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="p-6 rounded-2xl bg-neutral-950 border border-neutral-800 space-y-6">
          <div className="text-center space-y-1">
            <div className="w-10 h-10 rounded-xl bg-black border border-neutral-800 flex items-center justify-center mx-auto mb-2">
              <CheckCircle2 className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white">Diagnostic Complete</h2>
            <p className="text-xs text-neutral-400">Baseline calibrated successfully.</p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="p-3.5 rounded-xl bg-black border border-neutral-800 text-center">
              <div className="text-[11px] text-neutral-400">Score</div>
              <div className="text-xl font-bold text-white font-mono mt-0.5">
                {diagnosticResult.overall_score}%
              </div>
            </div>
            <div className="p-3.5 rounded-xl bg-black border border-neutral-800 text-center">
              <div className="text-[11px] text-neutral-400">Solved</div>
              <div className="text-xl font-bold text-white font-mono mt-0.5">
                {diagnosticResult.solved_count}/{diagnosticResult.total_count}
              </div>
            </div>
            <div className="p-3.5 rounded-xl bg-black border border-neutral-800 text-center">
              <div className="text-[11px] text-neutral-400">Starting Tier</div>
              <div className="text-xl font-bold text-white font-mono mt-0.5">
                {diagnosticResult.recommended_start_level}
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-black border border-neutral-800">
            <h4 className="text-[11px] font-mono font-bold uppercase text-neutral-400 mb-1">Summary</h4>
            <p className="text-xs text-neutral-300 leading-relaxed">
              {diagnosticResult.generated_plan_summary}
            </p>
          </div>

          <button
            onClick={() => router.push('/dashboard')}
            className="w-full py-2.5 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center justify-center space-x-1.5 transition-all shadow-sm"
          >
            <span>Go to Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    );
  }

  if (problems.length === 0) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex items-center space-x-2 text-neutral-400">
          <Activity className="w-4 h-4 animate-spin text-white" />
          <span className="text-xs font-mono">Loading diagnostic suite...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col bg-black overflow-hidden">
      {/* Top Header */}
      <div className="h-12 px-4 border-b border-neutral-800 bg-neutral-950 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-white text-xs">Diagnostic Test</span>
          <span className="text-xs text-neutral-600">|</span>
          <span className="text-xs text-neutral-400 font-mono">Q{currentIndex + 1} of {problems.length}</span>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center space-x-1 bg-black p-0.5 rounded-lg border border-neutral-800">
          {problems.map((p, idx) => (
            <button
              key={p.id}
              onClick={() => {
                setCurrentIndex(idx);
                setRunResult(null);
              }}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-all ${
                currentIndex === idx
                  ? 'bg-white text-black'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              Q{idx + 1} ({p.difficulty})
            </button>
          ))}
        </div>

        {/* Action button */}
        <button
          onClick={handleSubmitDiagnostic}
          disabled={submitting}
          className="px-3 py-1 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center space-x-1 transition-all"
        >
          <Send className="w-3 h-3" />
          <span>{submitting ? 'Submitting...' : 'Finish Test'}</span>
        </button>
      </div>

      {/* Split-Screen Arena */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 overflow-hidden">
        {/* Left: Problem Statement */}
        <div className="p-5 overflow-y-auto border-r border-neutral-800 bg-neutral-950 space-y-5">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-neutral-900 text-white border border-neutral-700">
                {currentProblem.difficulty}
              </span>
              <span className="text-[11px] text-neutral-400 font-mono">~{currentProblem.estimated_time_minutes}m</span>
            </div>
            <h1 className="text-base font-bold text-white">{currentProblem.title}</h1>
          </div>

          <div>
            <h3 className="text-[11px] font-mono font-bold uppercase text-neutral-400 mb-1.5">Problem Statement</h3>
            <FormattedContent content={currentProblem.statement} />
          </div>

          <div>
            <h3 className="text-[11px] font-mono font-bold uppercase text-neutral-400 mb-1.5">Input Format</h3>
            <div className="bg-black p-3 rounded-lg border border-neutral-800">
              <FormattedContent content={currentProblem.input_format} isMonoBlock />
            </div>
          </div>

          <div>
            <h3 className="text-[11px] font-mono font-bold uppercase text-neutral-400 mb-1.5">Output Format</h3>
            <div className="bg-black p-3 rounded-lg border border-neutral-800">
              <FormattedContent content={currentProblem.output_format} isMonoBlock />
            </div>
          </div>

          <div>
            <h3 className="text-[11px] font-mono font-bold uppercase text-neutral-400 mb-1.5">Constraints</h3>
            <div className="bg-black p-3 rounded-lg border border-neutral-800">
              <FormattedContent content={currentProblem.constraints} isMonoBlock />
            </div>
          </div>

          {currentProblem.examples && currentProblem.examples.length > 0 && (
            <div className="space-y-2.5">
              <h3 className="text-[11px] font-mono font-bold uppercase text-neutral-400">Examples</h3>
              {currentProblem.examples.map((ex: any, i: number) => (
                <div key={i} className="p-3 rounded-lg bg-black border border-neutral-800 space-y-1.5 text-xs font-mono">
                  <div>
                    <span className="text-neutral-500 font-semibold block">Input:</span>
                    <pre className="text-neutral-200 whitespace-pre-wrap">{ex.input}</pre>
                  </div>
                  <div>
                    <span className="text-neutral-500 font-semibold block">Output:</span>
                    <pre className="text-white font-bold whitespace-pre-wrap">{ex.output}</pre>
                  </div>
                  {ex.explanation && (
                    <div className="pt-1.5 border-t border-neutral-900">
                      <FormattedContent content={ex.explanation} className="text-[11px] text-neutral-400 italic" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Code Editor & Console Output */}
        <div className="flex flex-col h-full bg-black">
          {/* Editor Header */}
          <div className="h-10 px-3 border-b border-neutral-800 bg-neutral-950 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Code2 className="w-3.5 h-3.5 text-white" />
              <select
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="bg-black border border-neutral-800 text-xs text-white rounded px-2 py-0.5 focus:outline-none focus:border-neutral-500"
              >
                <option value="python">Python 3</option>
                <option value="cpp">C++ 17</option>
                <option value="java">Java 21</option>
                <option value="c">C 11</option>
              </select>
            </div>

            <button
              onClick={handleRun}
              disabled={isRunning}
              className="px-2.5 py-1 rounded bg-neutral-900 hover:bg-neutral-800 text-white border border-neutral-800 text-xs font-semibold flex items-center space-x-1 transition-all"
            >
              <Play className="w-3 h-3" />
              <span>{isRunning ? 'Running...' : 'Run Code'}</span>
            </button>
          </div>

          {/* Security Notice */}
          {securityNotice && (
            <div className="px-3 py-1.5 bg-neutral-900 border-b border-neutral-700 text-[11px] text-white flex items-center justify-between">
              <span>{securityNotice}</span>
              <button onClick={() => setSecurityNotice(null)} className="text-neutral-400 hover:text-white ml-2 text-xs">✕</button>
            </div>
          )}

          {/* Monaco Editor Container with Copy/Paste Prevention */}
          <div
            className="flex-1 min-h-[250px] relative"
            onPaste={(e) => { e.preventDefault(); triggerSecurityWarning(); }}
            onCopy={(e) => { e.preventDefault(); triggerSecurityWarning(); }}
            onCut={(e) => { e.preventDefault(); triggerSecurityWarning(); }}
            onContextMenu={(e) => { e.preventDefault(); }}
          >
            <MonacoEditor
              height="100%"
              language={language === 'c' || language === 'cpp' ? 'cpp' : language}
              theme="vs-dark"
              value={codes[currentProblem?.id] || ''}
              onChange={(value) => {
                if (currentProblem) {
                  setCodes(prev => ({ ...prev, [currentProblem.id]: value || '' }));
                }
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
                padding: { top: 8 },
                contextmenu: false,
                dragAndDrop: false,
              }}
            />
          </div>

          {/* Console Output */}
          <div className="h-40 border-t border-neutral-800 bg-neutral-950 p-3 overflow-y-auto font-mono text-xs">
            <div className="flex items-center justify-between text-neutral-500 text-[10px] mb-1.5 font-sans font-semibold">
              <span>OUTPUT CONSOLE</span>
              {runResult && (
                <span className={runResult.status === 'SUCCESS' ? 'text-white' : 'text-neutral-400'}>
                  {runResult.status} ({runResult.passed_count || 0}/{runResult.total_count || 0} passed)
                </span>
              )}
            </div>

            {runResult ? (
              <div className="space-y-1.5">
                {runResult.compiler_output && (
                  <pre className="text-neutral-300 bg-black p-2 rounded border border-neutral-800 whitespace-pre-wrap">
                    {runResult.compiler_output}
                  </pre>
                )}
                {runResult.test_case_results?.map((tc: any, i: number) => (
                  <div key={i} className="p-2 rounded bg-black border border-neutral-800 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-neutral-300">Case {tc.order_index}</span>
                      <span className={tc.status === 'PASSED' ? 'text-white font-bold' : 'text-neutral-400 font-bold'}>
                        {tc.status}
                      </span>
                    </div>
                    {tc.status !== 'PASSED' && (
                      <div className="mt-1 text-[11px] text-neutral-400 space-y-0.5">
                        <div>Expected: <span className="text-white">{tc.expected_output}</span></div>
                        <div>Got: <span className="text-neutral-300">{tc.actual_output}</span></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-neutral-600 text-[11px]">Click &apos;Run Code&apos; to execute against public test cases.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
