'use client';

import React, { useState } from 'react';
import { usePathname } from 'next/navigation';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const pathname = usePathname();

  const isStandalonePage =
    pathname === '/' ||
    pathname === '/login' ||
    pathname === '/register' ||
    pathname === '/onboarding' ||
    (pathname.includes('/mocks/') && pathname.includes('/take'));

  return (
    <div className="min-h-screen flex flex-col bg-black text-neutral-100 selection:bg-white selection:text-black">
      <Navbar onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)} />
      
      {!isStandalonePage && (
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      )}

      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          !isStandalonePage ? (sidebarCollapsed ? 'lg:pl-16' : 'lg:pl-64') : ''
        }`}
      >
        <main className="flex-grow">{children}</main>
        {!pathname.includes('/take') && <Footer />}
      </div>
    </div>
  );
}
