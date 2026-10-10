'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  Code2,
  Terminal,
  BrainCircuit,
  LayoutDashboard,
  Clock,
  Trophy,
  LogOut,
  Menu,
  X,
  PanelLeft,
  Sparkles,
  CalendarCheck,
  Target,
  AlertTriangle,
  RotateCcw,
  ShieldCheck
} from 'lucide-react';
import { User } from '@/types';

interface NavbarProps {
  onToggleSidebar?: () => void;
}

export default function Navbar({ onToggleSidebar }: NavbarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem('codevita_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        // ignore
      }
    }
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem('codevita_token');
    localStorage.removeItem('codevita_user');
    setUser(null);
    router.push('/login');
  };

  // Navigation links for mobile menu dropdown
  const mobileNavLinks = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/practice', label: 'Practice', icon: Terminal },
    { href: '/mocks', label: 'Mock Tests', icon: Clock },
    { href: '/ai-tutor', label: 'AI Coach', icon: BrainCircuit },
    { href: '/today', label: "Today's Focus", icon: Sparkles },
    { href: '/plan', label: 'Study Plan', icon: CalendarCheck },
    { href: '/diagnostic', label: 'Diagnostic Exam', icon: Target },
    { href: '/mistakes', label: 'Mistakes Notebook', icon: AlertTriangle },
    { href: '/reviews', label: 'Spaced Reviews', icon: RotateCcw },
    { href: '/leaderboard', label: 'Rankings', icon: Trophy },
  ];

  // If inside active mock exam take screen, hide top navbar
  if (pathname.includes('/mocks/') && pathname.includes('/take')) {
    return null;
  }

  const isStandalonePage =
    pathname === '/' ||
    pathname === '/login' ||
    pathname === '/register' ||
    pathname === '/onboarding';

  return (
    <nav className="sticky top-0 z-50 bg-black/95 backdrop-blur-md border-b border-neutral-800 h-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
        <div className="flex items-center justify-between h-full">
          {/* Brand Logo & Sidebar Trigger */}
          <div className="flex items-center space-x-3">
            {!isStandalonePage && onToggleSidebar && (
              <button
                onClick={onToggleSidebar}
                title="Toggle Sidebar"
                className="hidden lg:flex p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-900 border border-transparent hover:border-neutral-800 transition-colors mr-1"
              >
                <PanelLeft className="w-4 h-4" />
              </button>
            )}

            <Link href="/" className="flex items-center space-x-2.5 group">
              <div className="w-8 h-8 rounded-lg bg-white text-black flex items-center justify-center font-bold shadow-sm group-hover:scale-105 transition-transform">
                <Code2 className="w-4 h-4 text-black" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-base text-white tracking-tight leading-none group-hover:text-neutral-300 transition-colors">
                  CodeVita <span className="text-white font-mono text-[11px] font-semibold px-1.5 py-0.5 rounded bg-neutral-900 border border-neutral-700 ml-1">AI Coach</span>
                </span>
                <span className="text-[9px] text-neutral-400 tracking-wider uppercase font-mono mt-0.5">Adaptive CP Platform</span>
              </div>
            </Link>
          </div>

          {/* Right Action Area: Gamification & Profile */}
          <div className="hidden sm:flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                {/* XP & Level Badge */}
                <div className="flex items-center space-x-2 px-3 py-1 rounded-lg bg-neutral-950 border border-neutral-800">
                  <div className="flex items-center space-x-1 text-xs font-semibold text-neutral-200">
                    <Trophy className="w-3.5 h-3.5 text-white" />
                    <span>{user.xp || 0} XP</span>
                  </div>
                  <div className="w-px h-3.5 bg-neutral-800" />
                  <div className="flex items-center space-x-1 text-xs font-bold text-white">
                    <span>Lv.{user.level || 1}</span>
                  </div>
                </div>

                {/* Profile / Logout */}
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-medium text-neutral-300 max-w-[120px] truncate">
                    {user.full_name}
                  </span>
                  <button
                    onClick={handleLogout}
                    title="Logout"
                    className="p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-900 rounded-lg transition-colors border border-transparent hover:border-neutral-800"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  href="/login"
                  className="px-3.5 py-1.5 text-xs font-medium text-neutral-300 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-1.5 rounded-lg bg-white text-black hover:bg-neutral-200 text-xs font-semibold shadow-sm transition-all hover:scale-[1.02]"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu trigger */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-900"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-black border-b border-neutral-800 px-4 pt-2 pb-4 space-y-1">
          {mobileNavLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-medium ${
                  isActive ? 'bg-white text-black font-semibold' : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}

          {user?.role === 'ADMIN' && (
            <Link
              href="/admin"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-medium text-neutral-400 hover:text-white hover:bg-neutral-900"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Admin CMS</span>
            </Link>
          )}

          <div className="pt-3 border-t border-neutral-900 flex items-center justify-between">
            {user ? (
              <div className="flex items-center justify-between w-full">
                <span className="text-xs text-neutral-400">{user.full_name} ({user.xp} XP)</span>
                <button
                  onClick={handleLogout}
                  className="text-xs text-neutral-300 hover:text-white"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 w-full">
                <Link
                  href="/login"
                  className="flex-1 py-1.5 text-center text-xs text-neutral-300 bg-neutral-900 rounded-lg"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="flex-1 py-1.5 text-center text-xs text-black bg-white rounded-lg font-semibold"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
