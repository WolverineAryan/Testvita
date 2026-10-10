'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Terminal,
  Clock,
  BrainCircuit,
  Sparkles,
  CalendarCheck,
  Target,
  AlertTriangle,
  RotateCcw,
  Trophy,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  Flame,
  Zap,
  BookOpen
} from 'lucide-react';
import { User } from '@/types';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);

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

  // Hide sidebar on landing page, auth pages, and active mock take screen
  if (
    pathname === '/' ||
    pathname === '/login' ||
    pathname === '/register' ||
    pathname === '/onboarding' ||
    (pathname.includes('/mocks/') && pathname.includes('/take'))
  ) {
    return null;
  }

  const navGroups = [
    {
      title: 'CORE PLATFORM',
      items: [
        { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/practice', label: 'Practice Arena', icon: Terminal },
        { href: '/mocks', label: 'Mock Tests', icon: Clock },
        { href: '/ai-tutor', label: 'AI Socratic Coach', icon: BrainCircuit },
      ]
    },
    {
      title: 'ADAPTIVE PREPARATION',
      items: [
        { href: '/today', label: "Today's Focus", icon: Sparkles },
        { href: '/plan', label: 'Study Roadmap', icon: CalendarCheck },
        { href: '/diagnostic', label: 'Diagnostic Test', icon: Target },
      ]
    },
    {
      title: 'REVISION & MASTERY',
      items: [
        { href: '/mistakes', label: 'Mistake Notebook', icon: AlertTriangle },
        { href: '/reviews', label: 'Spaced Review', icon: RotateCcw },
        { href: '/leaderboard', label: 'Rankings & XP', icon: Trophy },
      ]
    }
  ];

  return (
    <aside
      className={`fixed top-16 left-0 bottom-0 z-40 bg-black border-r border-neutral-800 transition-all duration-300 flex flex-col justify-between ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {navGroups.map((group, groupIdx) => (
          <div key={groupIdx} className="space-y-1.5">
            {!collapsed && (
              <h4 className="px-3 text-[10px] font-mono uppercase tracking-wider text-neutral-500 font-semibold">
                {group.title}
              </h4>
            )}
            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    title={collapsed ? item.label : undefined}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-white text-black font-semibold shadow-sm'
                        : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
                    } ${collapsed ? 'justify-center px-2' : ''}`}
                  >
                    <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-black' : 'text-neutral-400'}`} />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}

        {/* Admin CMS link if role is ADMIN */}
        {user?.role === 'ADMIN' && (
          <div className="pt-2 border-t border-neutral-900 space-y-1.5">
            {!collapsed && (
              <h4 className="px-3 text-[10px] font-mono uppercase tracking-wider text-neutral-500 font-semibold">
                ADMINISTRATION
              </h4>
            )}
            <Link
              href="/admin"
              title={collapsed ? 'Admin CMS' : undefined}
              className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                pathname.startsWith('/admin')
                  ? 'bg-white text-black font-semibold'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              } ${collapsed ? 'justify-center px-2' : ''}`}
            >
              <ShieldCheck className={`w-4 h-4 shrink-0 ${pathname.startsWith('/admin') ? 'text-black' : 'text-neutral-400'}`} />
              {!collapsed && <span>Admin CMS</span>}
            </Link>
          </div>
        )}
      </div>

      {/* Footer / Collapse Toggle */}
      <div className="p-3 border-t border-neutral-900 flex items-center justify-between bg-neutral-950/80">
        {!collapsed && (
          <div className="flex items-center space-x-2 text-[11px] font-mono text-neutral-500">
            <Zap className="w-3.5 h-3.5 text-white" />
            <span>CodeVita S14 Ready</span>
          </div>
        )}
        <button
          onClick={onToggle}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          className={`p-1.5 text-neutral-400 hover:text-white hover:bg-neutral-900 rounded-lg transition-colors border border-transparent hover:border-neutral-800 ${
            collapsed ? 'mx-auto' : ''
          }`}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
