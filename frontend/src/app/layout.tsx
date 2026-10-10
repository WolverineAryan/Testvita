import type { Metadata } from 'next';
import './globals.css';
import AppShell from '@/components/AppShell';

export const metadata: Metadata = {
  title: 'CodeVita AI Coach — Adaptive Competitive Programming Platform',
  description: 'AI-powered preparation platform for TCS CodeVita with Monaco editor, secure sandbox execution, adaptive study planner, diagnostic assessment, and timed mock exams.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-black text-neutral-100 selection:bg-white selection:text-black">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
