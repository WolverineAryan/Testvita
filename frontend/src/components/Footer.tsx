import React from 'react';
import Link from 'next/link';
import { Code2, ShieldAlert } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-neutral-900 bg-black text-neutral-400 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-md bg-white text-black flex items-center justify-center font-bold">
              <Code2 className="w-4 h-4 text-black" />
            </div>
            <span className="font-bold text-white text-sm">CodeVita AI Coach</span>
          </div>

          <div className="flex flex-wrap gap-6 text-xs text-neutral-400">
            <Link href="/practice" className="hover:text-white transition-colors">Practice Arena</Link>
            <Link href="/mocks" className="hover:text-white transition-colors">Mock Tests</Link>
            <Link href="/diagnostic" className="hover:text-white transition-colors">Diagnostic Exam</Link>
            <Link href="/ai-tutor" className="hover:text-white transition-colors">AI Socratic Tutor</Link>
            <Link href="/leaderboard" className="hover:text-white transition-colors">Rankings</Link>
          </div>
        </div>

        {/* Independent Platform Disclaimer */}
        <div className="p-4 rounded-lg bg-neutral-950 border border-neutral-800/80 flex items-start space-x-3 text-xs text-neutral-400">
          <ShieldAlert className="w-4 h-4 text-neutral-300 shrink-0 mt-0.5" />
          <p>
            <strong className="text-white">Independent Preparation Platform:</strong> CodeVita AI Coach is an independent educational training platform developed to help engineering students build mastery in competitive programming and algorithmic problem-solving. All problem statements and test suites are original concepts.
          </p>
        </div>

        <div className="text-center text-[11px] text-neutral-500 font-mono">
          © {new Date().getFullYear()} CodeVita AI Coach. Adaptive Competitive Programming Platform.
        </div>
      </div>
    </footer>
  );
}
