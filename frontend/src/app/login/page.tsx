'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Code2, ArrowRight, Lock, Mail, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await api.post('/auth/login', { email, password });
      const { access_token, user_id, full_name, role } = res.data;
      
      localStorage.setItem('codevita_token', access_token);
      localStorage.setItem('codevita_user', JSON.stringify({ id: user_id, email, full_name, role }));

      // Fetch user profile to determine redirect
      const meRes = await api.get('/auth/me');
      const userObj = meRes.data;

      if (!userObj.profile?.onboarding_completed) {
        router.push('/onboarding');
      } else {
        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoStudent = () => {
    setEmail('student@codevita.ai');
    setPassword('student123');
  };

  const handleDemoAdmin = () => {
    setEmail('admin@codevita.ai');
    setPassword('admin123');
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full p-8 rounded-2xl bg-dark-900 border border-dark-800 shadow-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center mx-auto mb-3">
            <Code2 className="w-6 h-6 text-brand-400" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Welcome Back</h2>
          <p className="text-xs text-slate-400 mt-1">Sign in to resume your CodeVita training roadmap</p>
        </div>

        {/* Demo Quick Logins */}
        <div className="mb-6 p-3 rounded-xl bg-dark-800/80 border border-dark-700/80 text-xs flex items-center justify-between">
          <span className="text-slate-400 font-medium">Quick Demo Accounts:</span>
          <div className="space-x-2">
            <button
              type="button"
              onClick={handleDemoStudent}
              className="px-2.5 py-1 rounded bg-brand-600/30 hover:bg-brand-600/50 text-brand-300 font-semibold transition-colors"
            >
              Student
            </button>
            <button
              type="button"
              onClick={handleDemoAdmin}
              className="px-2.5 py-1 rounded bg-accent-amber/20 hover:bg-accent-amber/40 text-accent-amber font-semibold transition-colors"
            >
              Admin
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@university.edu"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-white text-sm placeholder:text-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-dark-950 border border-dark-700 text-white text-sm placeholder:text-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white font-semibold text-sm shadow-lg shadow-brand-600/25 flex items-center justify-center space-x-2 transition-all"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Arena'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-400">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-brand-400 hover:text-brand-300 font-semibold underline underline-offset-2">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
}
