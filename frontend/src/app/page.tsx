'use client';

import React from 'react';
import Link from 'next/link';
import {
  BrainCircuit,
  Terminal,
  Timer,
  ArrowRight,
  Activity,
  CheckCircle2
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-white selection:text-black">
      {/* Hero Section */}
      <section className="pt-20 pb-16 md:pt-28 md:pb-24 max-w-5xl mx-auto px-4 sm:px-6 text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-neutral-900 border border-neutral-800 text-neutral-300 text-xs font-mono mb-6">
          <span>TCS CodeVita Season 14</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Adaptive AI Coach for Competitive Programming
        </h1>

        <p className="mt-4 text-base sm:text-lg text-neutral-400 max-w-2xl mx-auto font-normal">
          Assess your baseline, target your algorithmic weaknesses, and follow a deterministic study roadmap tailored for CodeVita.
        </p>

        {/* Action CTAs */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/register"
            className="w-full sm:w-auto px-6 py-3 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs flex items-center justify-center space-x-2 transition-all shadow-sm"
          >
            <span>Start Preparing</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>

          <Link
            href="/diagnostic"
            className="w-full sm:w-auto px-6 py-3 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white border border-neutral-800 font-semibold text-xs flex items-center justify-center space-x-2 transition-all"
          >
            <Activity className="w-3.5 h-3.5 text-white" />
            <span>Diagnostic Test</span>
          </Link>
        </div>

        {/* Minimal Metrics Bar */}
        <div className="mt-14 pt-8 border-t border-neutral-800 grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
          <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800/80">
            <div className="text-xl font-bold text-white font-mono">50+</div>
            <div className="text-xs text-neutral-400 mt-0.5">Problems</div>
          </div>
          <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800/80">
            <div className="text-xl font-bold text-white font-mono">4 Langs</div>
            <div className="text-xs text-neutral-400 mt-0.5">C++, Python, Java, C</div>
          </div>
          <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800/80">
            <div className="text-xl font-bold text-white font-mono">Cloud Sandbox</div>
            <div className="text-xs text-neutral-400 mt-0.5">Instant Execution</div>
          </div>
          <div className="p-4 rounded-xl bg-neutral-950 border border-neutral-800/80">
            <div className="text-xl font-bold text-white font-mono">Timed Mocks</div>
            <div className="text-xs text-neutral-400 mt-0.5">Contest Simulation</div>
          </div>
        </div>
      </section>

      {/* Core Pillars */}
      <section className="py-14 border-t border-neutral-800 max-w-5xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-5 rounded-xl bg-neutral-950 border border-neutral-800">
            <BrainCircuit className="w-5 h-5 text-white mb-3" />
            <h3 className="text-sm font-bold text-white mb-1">Deterministic Skill Engine</h3>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Continuously tracks weighted mastery across arrays, graphs, trees, and dynamic programming based on submission history.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-neutral-950 border border-neutral-800">
            <Terminal className="w-5 h-5 text-white mb-3" />
            <h3 className="text-sm font-bold text-white mb-1">Online Code Editor</h3>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Monaco editor with cloud-backed execution, test case evaluation, and execution metrics.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-neutral-950 border border-neutral-800">
            <Timer className="w-5 h-5 text-white mb-3" />
            <h3 className="text-sm font-bold text-white mb-1">Contest Mocks</h3>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Full and mini mock assessments with server-enforced timers, rank tracking, and post-contest debriefs.
            </p>
          </div>
        </div>

        {/* Minimal Bottom CTA */}
        <div className="mt-14 p-6 rounded-xl bg-neutral-950 border border-neutral-800 text-center flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-left">
            <h3 className="text-sm font-bold text-white">Get Started with CodeVita AI Coach</h3>
            <p className="text-xs text-neutral-400 mt-0.5">Free diagnostic scan and personalized roadmap.</p>
          </div>
          <Link
            href="/register"
            className="px-5 py-2.5 rounded-lg bg-white hover:bg-neutral-200 text-black font-semibold text-xs transition-all shrink-0 shadow-sm"
          >
            Create Account
          </Link>
        </div>
      </section>
    </div>
  );
}
