import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { StudyPlan } from '@/types';

export function generateRoadmapPDF(plan: StudyPlan, userName?: string) {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 14;
  let y = 18;

  // Header Banner
  doc.setFillColor(15, 15, 15);
  doc.rect(margin, y, pageWidth - (margin * 2), 24, 'F');

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(16);
  doc.setTextColor(255, 255, 255);
  doc.text('CODEVITA AI COACH — TRAINING SYLLABUS & ROADMAP', margin + 6, y + 10);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(200, 200, 200);
  doc.text(
    `Official Algorithmic Preparation Blueprint | Candidate: ${userName || 'Active Learner'} | Generated: ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`,
    margin + 6,
    y + 17
  );

  y += 32;

  // Plan Overview Box
  const daysCount = plan.tasks?.length
    ? Math.max(...plan.tasks.map(t => t.day_number || 1))
    : 7;
  const totalMins = plan.tasks?.reduce((sum, t) => sum + (t.duration_minutes || 0), 0) || 0;
  const totalHours = (totalMins / 60).toFixed(1);
  const totalTasks = plan.tasks?.length || 0;
  const completedTasks = plan.tasks?.filter(t => t.is_completed).length || 0;

  doc.setDrawColor(220, 220, 220);
  doc.setFillColor(248, 248, 248);
  doc.roundedRect(margin, y, pageWidth - (margin * 2), 20, 2, 2, 'FD');

  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9);
  doc.setTextColor(30, 30, 30);

  const colWidth = (pageWidth - (margin * 2)) / 4;
  
  doc.text('PROGRAM DURATION', margin + 6, y + 8);
  doc.text('TOTAL STUDY TIME', margin + colWidth + 6, y + 8);
  doc.text('CURRICULUM TASKS', margin + (colWidth * 2) + 6, y + 8);
  doc.text('COMPLETION STATUS', margin + (colWidth * 3) + 6, y + 8);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(11);
  doc.setTextColor(0, 0, 0);
  doc.text(`${daysCount} Intensive Days`, margin + 6, y + 15);
  doc.text(`${totalHours} Hours (${totalMins}m)`, margin + colWidth + 6, y + 15);
  doc.text(`${totalTasks} Modules`, margin + (colWidth * 2) + 6, y + 15);
  doc.text(`${plan.completion_percentage || 0}% (${completedTasks}/${totalTasks})`, margin + (colWidth * 3) + 6, y + 15);

  y += 28;

  // Section 1: Executive Syllabus Overview
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  doc.setTextColor(15, 15, 15);
  doc.text('1. CORE CODEVITA SYLLABUS & COMPETENCY BREAKDOWN', margin, y);
  y += 4;

  const syllabusData = [
    [
      'Dynamic Programming\n(1D, 2D, Bitmask)',
      '0/1 & Unbounded Knapsack, Subsets, State Compression, Grid Paths, Longest Common Subsequence',
      'O(N*W) / O(N*2^N)\nSpace: O(N) opt',
      'High (35-40%)\nStandard Round 1 & 2'
    ],
    [
      'Graph Theory & Search\n(BFS, DFS, Dijkstra, Topo)',
      'Shortest Path in Weighted Grids, Topological Sort, Cycle Detection, Flood-fill, 0-1 BFS',
      'O(V + E log V)\nSpace: O(V + E)',
      'High (25-30%)\nGrid Traversal archetypes'
    ],
    [
      'Binary Search & Monotonic\nPredicates',
      'Binary Search on Answer Space, Monotonic Bounds (check(mid)), Lower/Upper Bound queries',
      'O(N log(Max-Min))\nSpace: O(1)',
      'Moderate-High (20%)\nOptimization problems'
    ],
    [
      'Arrays, Sliding Window &\nTwo Pointers',
      'Variable-length Window, Exact K Distinct, Converging Pointers, Prefix Sum Hash Map',
      'O(N) Time\nSpace: O(min(N, Alphabet))',
      'Fundamental (15-20%)\nDirect scoring problems'
    ],
    [
      'Trees, LCA & Disjoint Set\nUnion (DSU)',
      'Path Compression & Rank Union, Connected Components, Tree Diameter, Subtree DP',
      'O(α(N)) per DSU op\nSpace: O(V)',
      'Moderate (15%)\nNetwork connectivity'
    ],
    [
      'Number Theory & Modular\nArithmetic',
      'Sieve of Eratosthenes, Fast Modular Exponentiation (O(log exp)), Modular Multiplicative Inverse',
      'O(log N) / O(MAX log log MAX)\nSpace: O(MAX)',
      'Essential Support\nModulo 10^9+7 arithmetic'
    ]
  ];

  autoTable(doc, {
    startY: y,
    head: [['Algorithmic Domain', 'Key Subtopics & Invariants', 'Asymptotic Complexity', 'CodeVita Weightage']],
    body: syllabusData,
    theme: 'grid',
    headStyles: {
      fillColor: [30, 30, 30],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 8.5,
    },
    bodyStyles: {
      fontSize: 8,
      textColor: [40, 40, 40],
      cellPadding: 2.5,
    },
    columnStyles: {
      0: { cellWidth: 42, fontStyle: 'bold' },
      1: { cellWidth: 70 },
      2: { cellWidth: 38, fontStyle: 'normal' },
      3: { cellWidth: 32, fontStyle: 'bold' },
    },
    margin: { left: margin, right: margin },
  });

  // Calculate position after autoTable
  y = (doc as any).lastAutoTable.finalY + 12;

  // If running out of space, add new page
  if (y > pageHeight - 50) {
    doc.addPage();
    y = 18;
  }

  // Section 2: Personalized Day-by-Day Training Roadmap
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  doc.setTextColor(15, 15, 15);
  doc.text(`2. PERSONALIZED ${daysCount}-DAY TRAINING SCHEDULE`, margin, y);
  y += 4;

  const tasksData = (plan.tasks || []).map((task) => [
    `Day ${task.day_number}`,
    task.task_type.toUpperCase(),
    task.title,
    `${task.duration_minutes}m`,
    task.resource?.time_complexity || 'O(N) / O(V+E)',
    task.is_completed ? '[x] Done' : '[ ] Pending'
  ]);

  autoTable(doc, {
    startY: y,
    head: [['Schedule', 'Type', 'Task Title & Algorithmic Focus', 'Duration', 'Target Bounds', 'Status']],
    body: tasksData.length > 0 ? tasksData : [['Day 1', 'LEARN', 'Initial Diagnostic & Algorithm Setup', '60m', 'O(1)', '[ ] Pending']],
    theme: 'grid',
    headStyles: {
      fillColor: [30, 30, 30],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 8.5,
    },
    bodyStyles: {
      fontSize: 7.5,
      textColor: [40, 40, 40],
      cellPadding: 2.5,
    },
    columnStyles: {
      0: { cellWidth: 18, fontStyle: 'bold' },
      1: { cellWidth: 22, fontStyle: 'bold' },
      2: { cellWidth: 78 },
      3: { cellWidth: 18, fontStyle: 'normal' },
      4: { cellWidth: 28, fontStyle: 'normal' },
      5: { cellWidth: 18, fontStyle: 'bold' },
    },
    margin: { left: margin, right: margin },
  });

  y = (doc as any).lastAutoTable.finalY + 12;

  if (y > pageHeight - 65) {
    doc.addPage();
    y = 18;
  }

  // Section 3: CodeVita Contest Readiness Checklist
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  doc.setTextColor(15, 15, 15);
  doc.text('3. CODEVITA CONTEST EXECUTION PROTOCOL & STRATEGY', margin, y);
  y += 6;

  const strategies = [
    '• Time Budgeting: Scan all 6 problems in first 15 mins; solve easiest guaranteed Accepted first (typically Array/Greedy/BFS).',
    '• Constraint Verification: 10^5 operations require O(N) or O(N log N); 10^3 allows O(N^2); N <= 20 allows O(2^N) Bitmask DP.',
    '• Integer Overflow Safeguard: Use 64-bit integers (long long in C++, int64 in Python) for products, sums, and modular math.',
    '• Edge Case Invariants: Always test empty inputs, single element (N=1), extreme bounds, disjoint graphs, and all-equal arrays.',
    '• Adaptive AI Engine: Complete daily review queues to retain algorithmic patterns before taking full 3-hour mock tests.'
  ];

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8.5);
  doc.setTextColor(60, 60, 60);

  strategies.forEach((st) => {
    doc.text(st, margin, y);
    y += 5.5;
  });

  // Footer on all pages
  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setDrawColor(220, 220, 220);
    doc.line(margin, pageHeight - 12, pageWidth - margin, pageHeight - 12);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.5);
    doc.setTextColor(120, 120, 120);
    doc.text('CodeVita AI Coach — Automated Adaptive Training System', margin, pageHeight - 7);
    doc.text(`Page ${i} of ${totalPages}`, pageWidth - margin - 18, pageHeight - 7);
  }

  // Download the PDF
  doc.save(`CodeVita_Training_Roadmap_${daysCount}_Days.pdf`);
}
