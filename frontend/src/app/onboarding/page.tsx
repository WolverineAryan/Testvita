'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Code2,
  ArrowRight,
  CheckCircle2,
  Clock,
  Target,
  Sparkles,
  BookOpen,
  GraduationCap
} from 'lucide-react';
import { api } from '@/lib/api';

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Form states
  const [preferredLanguage, setPreferredLanguage] = useState('cpp');
  const [programmingExp, setProgrammingExp] = useState('INTERMEDIATE');
  const [cpExp, setCpExp] = useState('BEGINNER');
  const [college, setCollege] = useState('');
  const [gradYear, setGradYear] = useState('2026');
  const [dailyHours, setDailyHours] = useState(2.5);
  const [studyTime, setStudyTime] = useState('EVENING');
  const [targetCompetition, setTargetCompetition] = useState('TCS CodeVita');
  const [goal, setGoal] = useState('Crack CodeVita Round 1 & Round 2');

  const handleFinishOnboarding = async (goToDiagnostic: boolean) => {
    setLoading(true);
    try {
      await api.put('/auth/profile', {
        preferred_language: preferredLanguage,
        programming_experience: programmingExp,
        cp_experience: cpExp,
        college: college || 'Engineering Institute',
        graduation_year: parseInt(gradYear) || 2026,
        daily_available_hours: dailyHours,
        preferred_study_time: studyTime,
        target_competition: targetCompetition,
        preparation_goal: goal,
        onboarding_completed: true
      });

      if (goToDiagnostic) {
        router.push('/diagnostic');
      } else {
        router.push('/dashboard');
      }
    } catch (err) {
      console.error('Error saving onboarding profile:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full p-8 rounded-3xl bg-dark-900 border border-dark-800 shadow-2xl">
        {/* Progress Bar */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase text-brand-400">Step {step} of 4</span>
            <span className="text-slate-600">•</span>
            <span className="text-xs text-slate-400">Profile Calibration</span>
          </div>
          <div className="flex space-x-1.5">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={`h-1.5 w-8 rounded-full transition-all ${
                  step >= i ? 'bg-brand-500' : 'bg-dark-700'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Step 1: Programming Language */}
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Select Your Primary Language</h2>
            <p className="text-xs text-slate-400 mb-6">
              Choose the language you are most fluent in for CodeVita problem-solving.
            </p>

            <div className="grid grid-cols-2 gap-4 mb-8">
              {[
                { id: 'cpp', name: 'C++ (C++17 / STL)', desc: 'Optimal execution speed & rich STL algorithms' },
                { id: 'python', name: 'Python (Python 3.10+)', desc: 'Fast prototyping & clean data structures' },
                { id: 'java', name: 'Java (OpenJDK 21)', desc: 'Strong typing & robust Collections framework' },
                { id: 'c', name: 'C (C11)', desc: 'Low-level memory efficiency & speed' }
              ].map((lang) => (
                <button
                  key={lang.id}
                  type="button"
                  onClick={() => setPreferredLanguage(lang.id)}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    preferredLanguage === lang.id
                      ? 'bg-brand-600/20 border-brand-500 text-white shadow-lg shadow-brand-600/10'
                      : 'bg-dark-800/50 border-dark-700 text-slate-300 hover:border-dark-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm">{lang.name}</span>
                    {preferredLanguage === lang.id && <CheckCircle2 className="w-4 h-4 text-brand-400" />}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{lang.desc}</p>
                </button>
              ))}
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm flex items-center justify-center space-x-2 transition-all"
            >
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Step 2: Experience & College */}
        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Coding Experience & Background</h2>
            <p className="text-xs text-slate-400 mb-6">
              This helps calibrate your baseline algorithmic problem recommendations.
            </p>

            <div className="space-y-4 mb-8">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Competitive Programming Background</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: 'BEGINNER', label: 'Beginner', desc: 'New to CP contests' },
                    { id: 'INTERMEDIATE', label: 'Intermediate', desc: 'Solved 50+ LeetCode/GFG' },
                    { id: 'ADVANCED', label: 'Advanced', desc: 'Active Codeforces/CodeChef' }
                  ].map((exp) => (
                    <button
                      key={exp.id}
                      type="button"
                      onClick={() => setCpExp(exp.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        cpExp === exp.id
                          ? 'bg-brand-600/20 border-brand-500 text-white'
                          : 'bg-dark-800/50 border-dark-700 text-slate-300'
                      }`}
                    >
                      <div className="font-bold text-xs">{exp.label}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">{exp.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">College / University</label>
                  <input
                    type="text"
                    value={college}
                    onChange={(e) => setCollege(e.target.value)}
                    placeholder="e.g. National Institute of Tech"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-white text-xs placeholder:text-slate-600 focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Graduation Year</label>
                  <select
                    value={gradYear}
                    onChange={(e) => setGradYear(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-white text-xs focus:outline-none focus:border-brand-500"
                  >
                    <option value="2025">2025</option>
                    <option value="2026">2026</option>
                    <option value="2027">2027</option>
                    <option value="2028">2028</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setStep(1)}
                className="py-3 px-5 rounded-xl bg-dark-800 hover:bg-dark-700 text-slate-300 text-sm font-semibold"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex-1 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm flex items-center justify-center space-x-2"
              >
                <span>Continue</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Daily Available Hours & Time */}
        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Daily Preparation Schedule</h2>
            <p className="text-xs text-slate-400 mb-6">
              The AI planner will allocate drills to match your daily available time.
            </p>

            <div className="space-y-6 mb-8">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-xs font-semibold text-slate-300">Daily Study Hours</label>
                  <span className="text-sm font-bold text-brand-400 font-mono">{dailyHours} Hours/Day</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="8"
                  step="0.5"
                  value={dailyHours}
                  onChange={(e) => setDailyHours(parseFloat(e.target.value))}
                  className="w-full accent-brand-500 bg-dark-950 h-2 rounded-lg cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2">Preferred Study Period</label>
                <div className="grid grid-cols-4 gap-2">
                  {['MORNING', 'AFTERNOON', 'EVENING', 'NIGHT'].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setStudyTime(p)}
                      className={`p-3 rounded-xl border text-center text-xs font-bold transition-all ${
                        studyTime === p
                          ? 'bg-brand-600/20 border-brand-500 text-white'
                          : 'bg-dark-800/50 border-dark-700 text-slate-400'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setStep(2)}
                className="py-3 px-5 rounded-xl bg-dark-800 hover:bg-dark-700 text-slate-300 text-sm font-semibold"
              >
                Back
              </button>
              <button
                onClick={() => setStep(4)}
                className="flex-1 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm flex items-center justify-center space-x-2"
              >
                <span>Continue</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Final Calibration & Diagnostic Test Prompt */}
        {step === 4 && (
          <div>
            <div className="p-4 rounded-2xl bg-brand-600/10 border border-brand-500/30 text-center mb-6">
              <Sparkles className="w-8 h-8 text-accent-cyan mx-auto mb-2 animate-bounce" />
              <h3 className="text-lg font-bold text-white">Unlock Your Adaptive AI Roadmap</h3>
              <p className="text-xs text-slate-300 mt-1 max-w-md mx-auto">
                Take the 15-minute Diagnostic Assessment (3 problems) to evaluate your current baseline and generate your tailored study plan.
              </p>
            </div>

            <div className="space-y-3 mb-6">
              <button
                onClick={() => handleFinishOnboarding(true)}
                disabled={loading}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-accent-cyan hover:opacity-90 text-white font-bold text-sm shadow-xl flex items-center justify-center space-x-2"
              >
                <span>Take Diagnostic Assessment (Recommended)</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => handleFinishOnboarding(false)}
                disabled={loading}
                className="w-full py-3 rounded-xl bg-dark-800 hover:bg-dark-700 text-slate-400 hover:text-slate-200 text-xs font-semibold"
              >
                Skip Diagnostic for now (Generate default plan)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
