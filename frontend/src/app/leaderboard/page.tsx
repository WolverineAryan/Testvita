'use client';

import React, { useState, useEffect } from 'react';
import {
  Trophy,
  Activity
} from 'lucide-react';
import { api } from '@/lib/api';

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [achievements, setAchievements] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'rankings' | 'achievements'>('rankings');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [leadRes, achRes] = await Promise.allSettled([
          api.get('/analytics/leaderboard'),
          api.get('/analytics/achievements')
        ]);
        if (leadRes.status === 'fulfilled') setLeaderboard(leadRes.value.data);
        if (achRes.status === 'fulfilled') setAchievements(achRes.value.data);
      } catch (e) {
        console.error('Error loading leaderboard:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex items-center space-x-2 text-neutral-400">
          <Activity className="w-4 h-4 animate-spin text-white" />
          <span className="text-xs font-mono">Loading rankings...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-neutral-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Leaderboard</h1>
          <p className="text-xs text-neutral-400 mt-0.5">
            Rankings and achievement badges.
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex items-center space-x-1 bg-neutral-900 p-1 rounded-lg border border-neutral-800">
          <button
            onClick={() => setActiveTab('rankings')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeTab === 'rankings'
                ? 'bg-white text-black'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Rankings
          </button>
          <button
            onClick={() => setActiveTab('achievements')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-all ${
              activeTab === 'achievements'
                ? 'bg-white text-black'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Badges
          </button>
        </div>
      </div>

      {activeTab === 'rankings' ? (
        <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-neutral-400 border-b border-neutral-800">
                <tr>
                  <th className="py-2.5 px-3">Rank</th>
                  <th className="py-2.5 px-3">Candidate</th>
                  <th className="py-2.5 px-3">Level</th>
                  <th className="py-2.5 px-3 text-right">XP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-850">
                {leaderboard.map((u) => (
                  <tr key={u.user_id} className="hover:bg-neutral-900/50 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-white">
                      #{u.rank}
                    </td>
                    <td className="py-3 px-3 font-medium text-neutral-200">
                      {u.display_name}
                    </td>
                    <td className="py-3 px-3 font-mono text-neutral-400">
                      Lv. {u.level}
                    </td>
                    <td className="py-3 px-3 text-right font-mono font-bold text-white">
                      {u.xp} XP
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {achievements.map((ach) => (
            <div
              key={ach.id}
              className={`p-3.5 rounded-xl border flex items-start space-x-3 transition-all ${
                ach.is_unlocked
                  ? 'bg-neutral-950 border-neutral-700'
                  : 'bg-neutral-950/40 border-neutral-900 opacity-40'
              }`}
            >
              <div className="w-8 h-8 rounded-lg bg-black border border-neutral-800 flex items-center justify-center shrink-0">
                <Trophy className="w-4 h-4 text-white" />
              </div>

              <div className="space-y-0.5">
                <h3 className="text-xs font-bold text-white">{ach.title}</h3>
                <p className="text-[11px] text-neutral-400">{ach.description}</p>
                <div className="text-[10px] text-neutral-500 font-mono">+{ach.xp_reward} XP</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
