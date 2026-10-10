'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ShieldCheck,
  PlusCircle,
  Database,
  Layers,
  Activity,
  CheckCircle2,
  AlertCircle,
  Save,
  Clock,
  Sparkles
} from 'lucide-react';
import { api } from '@/lib/api';

export default function AdminCMSPage() {
  const router = useRouter();
  const [metrics, setMetrics] = useState<any>(null);
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'metrics' | 'create_problem' | 'create_mock' | 'announcement'>('metrics');

  // Problem Form State
  const [problemTitle, setProblemTitle] = useState('');
  const [difficulty, setDifficulty] = useState('MEDIUM');
  const [timeLimit, setTimeLimit] = useState(2.0);
  const [memoryLimit, setMemoryLimit] = useState(256);
  const [selectedTopicId, setSelectedTopicId] = useState('');
  const [statement, setStatement] = useState('');
  const [inputFormat, setInputFormat] = useState('');
  const [outputFormat, setOutputFormat] = useState('');
  const [constraints, setConstraints] = useState('');
  const [publicInput, setPublicInput] = useState('');
  const [publicOutput, setPublicOutput] = useState('');
  const [hiddenInput, setHiddenInput] = useState('');
  const [hiddenOutput, setHiddenOutput] = useState('');
  const [hintTitle, setHintTitle] = useState('');
  const [hintContent, setHintContent] = useState('');
  const [problemSuccess, setProblemSuccess] = useState('');

  // Announcement State
  const [annTitle, setAnnTitle] = useState('');
  const [annContent, setAnnContent] = useState('');
  const [annType, setAnnType] = useState('PLATFORM_UPDATE');
  const [annSuccess, setAnnSuccess] = useState('');

  useEffect(() => {
    async function loadAdminData() {
      try {
        const [metricRes, topicRes] = await Promise.allSettled([
          api.get('/admin/metrics'),
          api.get('/problems/topics')
        ]);

        if (metricRes.status === 'fulfilled') setMetrics(metricRes.value.data);
        if (topicRes.status === 'fulfilled') {
          setTopics(topicRes.value.data);
          if (topicRes.value.data.length > 0) setSelectedTopicId(topicRes.value.data[0].id);
        }
      } catch (e: any) {
        if (e.response?.status === 403) {
          router.push('/dashboard');
        }
      } finally {
        setLoading(false);
      }
    }
    loadAdminData();
  }, [router]);

  const handleCreateProblem = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblemSuccess('');
    try {
      await api.post('/admin/problems', {
        title: problemTitle,
        difficulty,
        difficulty_score: difficulty === 'EASY' ? 30 : difficulty === 'MEDIUM' ? 60 : 85,
        estimated_time_minutes: difficulty === 'EASY' ? 20 : difficulty === 'MEDIUM' ? 35 : 50,
        time_limit_seconds: timeLimit,
        memory_limit_mb: memoryLimit,
        topic_ids: selectedTopicId ? [selectedTopicId] : [],
        statement,
        input_format: inputFormat,
        output_format: outputFormat,
        constraints,
        examples: [{ input: publicInput, output: publicOutput, explanation: 'Sample test case.' }],
        public_test_cases: [{ input_data: publicInput, expected_output: publicOutput, order_index: 1, is_hidden: false }],
        hidden_test_cases: [{ input_data: hiddenInput, expected_output: hiddenOutput, order_index: 2, is_hidden: true }],
        hints: hintTitle ? [{ order_index: 1, title: hintTitle, content: hintContent }] : []
      });

      setProblemSuccess('Problem published successfully to Practice Arena!');
      setProblemTitle('');
      setStatement('');
      setInputFormat('');
      setOutputFormat('');
      setConstraints('');
      setPublicInput('');
      setPublicOutput('');
      setHiddenInput('');
      setHiddenOutput('');
    } catch (err) {
      console.error('Failed to create problem:', err);
    }
  };

  const handleCreateAnnouncement = async (e: React.FormEvent) => {
    e.preventDefault();
    setAnnSuccess('');
    try {
      await api.post('/admin/announcements', {
        title: annTitle,
        content: annContent,
        announcement_type: annType,
        is_pinned: false
      });
      setAnnSuccess('Announcement broadcasted to all students!');
      setAnnTitle('');
      setAnnContent('');
    } catch (err) {
      console.error('Failed to create announcement:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="flex items-center space-x-3 text-slate-400">
          <ShieldCheck className="w-6 h-6 animate-spin text-accent-amber" />
          <span className="text-sm font-medium">Validating Administrator Privileges...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold uppercase text-accent-amber mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Platform Content & Assessment Management</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Admin CMS Panel</h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Author original algorithmic problems, configure test suites, and manage mock contest rounds.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center space-x-1.5 bg-dark-900 p-1.5 rounded-xl border border-dark-800 text-xs">
          <button
            onClick={() => setActiveTab('metrics')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              activeTab === 'metrics' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            System Metrics
          </button>
          <button
            onClick={() => setActiveTab('create_problem')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              activeTab === 'create_problem' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            + Author Problem
          </button>
          <button
            onClick={() => setActiveTab('announcement')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              activeTab === 'announcement' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Announcements
          </button>
        </div>
      </div>

      {/* Metrics View */}
      {activeTab === 'metrics' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-dark-900 border border-dark-800">
              <div className="text-xs text-slate-400">Total Registered Users</div>
              <div className="text-2xl font-bold text-white font-mono mt-1">{metrics?.total_users || 0}</div>
            </div>
            <div className="p-5 rounded-2xl bg-dark-900 border border-dark-800">
              <div className="text-xs text-slate-400">Problems in Bank</div>
              <div className="text-2xl font-bold text-accent-cyan font-mono mt-1">{metrics?.total_problems || 0}</div>
            </div>
            <div className="p-5 rounded-2xl bg-dark-900 border border-dark-800">
              <div className="text-xs text-slate-400">Evaluated Submissions</div>
              <div className="text-2xl font-bold text-accent-emerald font-mono mt-1">{metrics?.total_submissions || 0}</div>
            </div>
            <div className="p-5 rounded-2xl bg-dark-900 border border-dark-800">
              <div className="text-xs text-slate-400">Total Mocks Completed</div>
              <div className="text-2xl font-bold text-accent-amber font-mono mt-1">{metrics?.total_mocks_taken || 0}</div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-800 flex items-center justify-between">
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-white">System Status & Sandbox Execution Engine</h3>
              <p className="text-xs text-slate-400">{metrics?.system_health || 'Operating normally with Docker/Subprocess sandboxing.'}</p>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold uppercase">
              Operational
            </span>
          </div>
        </div>
      )}

      {/* Create Problem View */}
      {activeTab === 'create_problem' && (
        <form onSubmit={handleCreateProblem} className="p-8 rounded-3xl bg-dark-900 border border-dark-800 shadow-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-dark-800 pb-4">
            <div className="flex items-center space-x-2">
              <PlusCircle className="w-5 h-5 text-accent-cyan" />
              <h2 className="text-lg font-bold text-white">Author New Problem</h2>
            </div>
            {problemSuccess && (
              <span className="text-xs font-bold text-accent-emerald flex items-center space-x-1">
                <CheckCircle2 className="w-4 h-4" /> <span>{problemSuccess}</span>
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Problem Title</label>
              <input
                type="text"
                required
                value={problemTitle}
                onChange={(e) => setProblemTitle(e.target.value)}
                placeholder="e.g. Dynamic Component Bridging"
                className="w-full px-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-brand-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
              >
                <option value="EASY">EASY</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HARD">HARD</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Primary Topic</label>
              <select
                value={selectedTopicId}
                onChange={(e) => setSelectedTopicId(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
              >
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Time Limit (Seconds)</label>
              <input
                type="number"
                step="0.5"
                value={timeLimit}
                onChange={(e) => setTimeLimit(parseFloat(e.target.value))}
                className="w-full px-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Memory Limit (MB)</label>
              <input
                type="number"
                value={memoryLimit}
                onChange={(e) => setMemoryLimit(parseInt(e.target.value))}
                className="w-full px-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Problem Statement</label>
            <textarea
              rows={4}
              required
              value={statement}
              onChange={(e) => setStatement(e.target.value)}
              placeholder="Detailed algorithmic problem statement..."
              className="w-full px-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-brand-500 font-sans"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Input Format</label>
              <textarea
                rows={2}
                value={inputFormat}
                onChange={(e) => setInputFormat(e.target.value)}
                placeholder="Input format specifications..."
                className="w-full px-3 py-2 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Output Format</label>
              <textarea
                rows={2}
                value={outputFormat}
                onChange={(e) => setOutputFormat(e.target.value)}
                placeholder="Output format specifications..."
                className="w-full px-3 py-2 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Constraints</label>
              <textarea
                rows={2}
                value={constraints}
                onChange={(e) => setConstraints(e.target.value)}
                placeholder="1 <= N <= 10^5..."
                className="w-full px-3 py-2 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          {/* Test Cases */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-dark-800">
            <div>
              <label className="block text-xs font-bold text-accent-cyan mb-1.5">Public Sample Input</label>
              <textarea
                rows={2}
                value={publicInput}
                onChange={(e) => setPublicInput(e.target.value)}
                placeholder="Public sample input..."
                className="w-full px-3 py-2 rounded-xl bg-dark-950 border border-dark-700 text-xs font-mono text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-accent-cyan mb-1.5">Public Sample Output</label>
              <textarea
                rows={2}
                value={publicOutput}
                onChange={(e) => setPublicOutput(e.target.value)}
                placeholder="Public sample output..."
                className="w-full px-3 py-2 rounded-xl bg-dark-950 border border-dark-700 text-xs font-mono text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-accent-amber mb-1.5">Hidden Grading Input</label>
              <textarea
                rows={2}
                value={hiddenInput}
                onChange={(e) => setHiddenInput(e.target.value)}
                placeholder="Hidden evaluation input..."
                className="w-full px-3 py-2 rounded-xl bg-dark-950 border border-dark-700 text-xs font-mono text-white focus:outline-none focus:border-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-accent-amber mb-1.5">Hidden Grading Output</label>
              <textarea
                rows={2}
                value={hiddenOutput}
                onChange={(e) => setHiddenOutput(e.target.value)}
                placeholder="Hidden evaluation output..."
                className="w-full px-3 py-2 rounded-xl bg-dark-950 border border-dark-700 text-xs font-mono text-white focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs shadow-lg shadow-brand-600/25 flex items-center justify-center space-x-2 transition-all hover:scale-[1.01]"
          >
            <Save className="w-4 h-4" />
            <span>Publish Problem to Platform</span>
          </button>
        </form>
      )}

      {/* Announcements */}
      {activeTab === 'announcement' && (
        <form onSubmit={handleCreateAnnouncement} className="p-8 rounded-3xl bg-dark-900 border border-dark-800 shadow-2xl space-y-4">
          <h2 className="text-lg font-bold text-white mb-2">Publish Platform Announcement</h2>
          {annSuccess && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
              {annSuccess}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Title</label>
            <input
              type="text"
              required
              value={annTitle}
              onChange={(e) => setAnnTitle(e.target.value)}
              placeholder="e.g. New Dynamic Programming Track Live"
              className="w-full px-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Content</label>
            <textarea
              rows={3}
              required
              value={annContent}
              onChange={(e) => setAnnContent(e.target.value)}
              placeholder="Announcement details..."
              className="w-full px-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-xs text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-xs"
          >
            Broadcast Announcement
          </button>
        </form>
      )}
    </div>
  );
}
