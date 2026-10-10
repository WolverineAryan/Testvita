'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Search,
  CheckCircle2,
  Clock,
  Bookmark,
  BookmarkCheck,
  ChevronRight,
  Activity,
  X,
  Filter
} from 'lucide-react';
import { api } from '@/lib/api';
import { getDifficultyColor } from '@/lib/utils';
import { ProblemListItem, Topic } from '@/types';

function PracticeContent() {
  const searchParams = useSearchParams();
  const urlTopic = searchParams.get('topic') || '';

  const [problems, setProblems] = useState<ProblemListItem[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [search, setSearch] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(urlTopic);
  const [selectedStatus, setSelectedStatus] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = searchParams.get('topic');
    if (t) {
      setSelectedTopic(t);
    }
  }, [searchParams]);

  useEffect(() => {
    async function fetchTopics() {
      try {
        const res = await api.get('/problems/topics');
        setTopics(res.data);
      } catch (e) {
        console.error('Error loading topics:', e);
      }
    }
    fetchTopics();
  }, []);

  useEffect(() => {
    async function fetchProblems() {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (selectedDifficulty) params.append('difficulty', selectedDifficulty);
        if (selectedTopic) params.append('topic', selectedTopic);
        if (selectedStatus) params.append('status', selectedStatus);

        const res = await api.get(`/problems?${params.toString()}`);
        setProblems(res.data.problems || []);
      } catch (e) {
        console.error('Error fetching problems:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchProblems();
  }, [search, selectedDifficulty, selectedTopic, selectedStatus]);

  const handleToggleBookmark = async (e: React.MouseEvent, problemId: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      const res = await api.post(`/problems/${problemId}/bookmark`);
      setProblems(prev =>
        prev.map(p => (p.id === problemId ? { ...p, is_bookmarked: res.data.bookmarked } : p))
      );
    } catch (e) {
      console.error('Error toggling bookmark:', e);
    }
  };

  // Find readable topic label if slug is selected
  const activeTopicObj = topics.find(
    t => t.slug === selectedTopic || t.name.toLowerCase() === selectedTopic.toLowerCase()
  );
  const activeTopicDisplay = activeTopicObj ? activeTopicObj.name : selectedTopic;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-neutral-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Practice Problems</h1>
          <p className="text-xs text-neutral-400 mt-0.5">
            Algorithmic problem set for TCS CodeVita preparation.
          </p>
        </div>

        {/* Status Filter */}
        <div className="flex items-center space-x-1 bg-neutral-900 p-1 rounded-lg border border-neutral-800">
          {[
            { id: '', label: 'All' },
            { id: 'unsolved', label: 'Unsolved' },
            { id: 'solved', label: 'Solved' }
          ].map((st) => (
            <button
              key={st.id}
              onClick={() => setSelectedStatus(st.id)}
              className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
                selectedStatus === st.id
                  ? 'bg-white text-black'
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>
      </div>

      {/* Active Filter Pill */}
      {selectedTopic && (
        <div className="flex items-center justify-between p-3 rounded-xl bg-neutral-950 border border-neutral-800">
          <div className="flex items-center space-x-2 text-xs text-neutral-300">
            <Filter className="w-3.5 h-3.5 text-white" />
            <span>Showing problems for topic:</span>
            <span className="px-2 py-0.5 rounded bg-white text-black font-bold font-mono text-[11px]">
              {activeTopicDisplay}
            </span>
          </div>
          <button
            onClick={() => setSelectedTopic('')}
            className="text-xs text-neutral-400 hover:text-white flex items-center space-x-1 px-2 py-1 rounded hover:bg-neutral-900 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
            <span>Clear topic filter</span>
          </button>
        </div>
      )}

      {/* Filter Bar */}
      <div className="p-3 rounded-xl bg-neutral-950 border border-neutral-800 grid grid-cols-1 sm:grid-cols-4 gap-2.5">
        <div className="sm:col-span-2 relative">
          <Search className="w-3.5 h-3.5 text-neutral-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search problems..."
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-black border border-neutral-800 text-xs text-white placeholder:text-neutral-600 focus:outline-none focus:border-neutral-500"
          />
        </div>

        <div>
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="w-full px-2.5 py-1.5 rounded-lg bg-black border border-neutral-800 text-xs text-neutral-300 focus:outline-none focus:border-neutral-500"
          >
            <option value="">All Difficulties</option>
            <option value="EASY">Easy</option>
            <option value="MEDIUM">Medium</option>
            <option value="HARD">Hard</option>
          </select>
        </div>

        <div>
          <select
            value={activeTopicObj ? activeTopicObj.slug : selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value)}
            className="w-full px-2.5 py-1.5 rounded-lg bg-black border border-neutral-800 text-xs text-neutral-300 focus:outline-none focus:border-neutral-500"
          >
            <option value="">All Topics</option>
            {topics.map((t) => (
              <option key={t.id} value={t.slug}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Problems List */}
      {loading ? (
        <div className="py-16 text-center">
          <Activity className="w-5 h-5 animate-spin text-white mx-auto mb-2" />
          <p className="text-xs text-neutral-500 font-mono">Loading problems...</p>
        </div>
      ) : problems.length === 0 ? (
        <div className="py-12 text-center bg-neutral-950 rounded-xl border border-neutral-800 p-6 space-y-2">
          <p className="text-xs text-neutral-400">No matching problems found for {activeTopicDisplay || 'the selected criteria'}.</p>
          {selectedTopic && (
            <button
              onClick={() => setSelectedTopic('')}
              className="text-xs text-white underline underline-offset-4 hover:text-neutral-300 transition-colors"
            >
              View all practice problems
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {problems.map((p) => {
            const diffStyle = getDifficultyColor(p.difficulty);
            return (
              <Link
                key={p.id}
                href={`/practice/${p.slug}`}
                className="flex items-center justify-between p-3.5 rounded-lg bg-neutral-950 border border-neutral-800/80 hover:border-neutral-600 transition-colors group gap-4"
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <div className="shrink-0">
                    {p.is_solved ? (
                      <CheckCircle2 className="w-4 h-4 text-white" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-neutral-700 bg-neutral-900" />
                    )}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-xs font-bold text-white group-hover:text-neutral-300 transition-colors truncate">
                        {p.title}
                      </h3>
                      <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${diffStyle.bg} ${diffStyle.text} ${diffStyle.border}`}>
                        {p.difficulty}
                      </span>
                    </div>

                    <div className="flex items-center space-x-1.5 mt-0.5">
                      {p.topics?.slice(0, 3).map((topic, i) => (
                        <span key={i} className="text-[10px] text-neutral-500 font-mono">
                          #{topic}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4 shrink-0">
                  <span className="text-[11px] text-neutral-400 font-mono flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-neutral-500" />
                    <span>{p.estimated_time_minutes}m</span>
                  </span>

                  <button
                    onClick={(e) => handleToggleBookmark(e, p.id)}
                    className="p-1 rounded text-neutral-500 hover:text-white transition-colors"
                  >
                    {p.is_bookmarked ? (
                      <BookmarkCheck className="w-3.5 h-3.5 text-white" />
                    ) : (
                      <Bookmark className="w-3.5 h-3.5" />
                    )}
                  </button>

                  <ChevronRight className="w-3.5 h-3.5 text-neutral-600 group-hover:text-white transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function PracticePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[60vh] flex items-center justify-center">
          <Activity className="w-4 h-4 animate-spin text-white" />
        </div>
      }
    >
      <PracticeContent />
    </Suspense>
  );
}
