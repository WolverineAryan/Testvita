'use client';

import React from 'react';

interface FormattedContentProps {
  content?: string | null;
  className?: string;
  isMonoBlock?: boolean;
}

// Map digits to unicode superscripts
const SUPERSCRIPTS: Record<string, string> = {
  '0': '⁰',
  '1': '¹',
  '2': '²',
  '3': '³',
  '4': '⁴',
  '5': '⁵',
  '6': '⁶',
  '7': '⁷',
  '8': '⁸',
  '9': '⁹',
  '+': '⁺',
  '-': '⁻',
  '=': '⁼',
  '(': '⁽',
  ')': '⁾',
  'n': 'ⁿ',
  'i': 'ⁱ',
  'k': 'ᵏ'
};

export function cleanMathText(text: string): string {
  let res = text;
  // Replace LaTeX comparison & logic operators
  res = res.replace(/\\le\b|\\leq\b/g, '≤');
  res = res.replace(/\\ge\b|\\geq\b/g, '≥');
  res = res.replace(/\\ne\b|\\neq\b/g, '≠');
  res = res.replace(/\\approx\b/g, '≈');
  res = res.replace(/\\times\b/g, '×');
  res = res.replace(/\\cdot\b/g, '·');
  res = res.replace(/\\dots\b|\\ldots\b/g, '…');
  res = res.replace(/\\in\b/g, '∈');
  res = res.replace(/\\notin\b/g, '∉');
  res = res.replace(/\\forall\b/g, '∀');
  res = res.replace(/\\exists\b/g, '∃');
  res = res.replace(/\\infty\b/g, '∞');
  res = res.replace(/\\pm\b/g, '±');
  res = res.replace(/\\log\b/g, 'log');

  // Replace powers like 10^5, 10^9+7, 2^31-1
  res = res.replace(/\^(\d+)/g, (_, digits) => {
    return digits.split('').map((d: string) => SUPERSCRIPTS[d] || d).join('');
  });
  res = res.replace(/\^\{([^}]+)\}/g, (_, exp) => {
    return exp.split('').map((d: string) => SUPERSCRIPTS[d] || d).join('');
  });

  return res;
}

interface InlineToken {
  type: 'text' | 'math' | 'code' | 'bold' | 'italic';
  val: string;
}

function parseInline(rawText: string): InlineToken[] {
  const tokens: InlineToken[] = [];
  let remaining = rawText;

  while (remaining.length > 0) {
    const mathMatch = remaining.match(/^(\$([^\$]+)\$)/);
    const codeMatch = remaining.match(/^(`([^`]+)`)/);
    const boldMatch = remaining.match(/^(\*\*([^*]+)\*\*)/);
    const italicMatch = remaining.match(/^(\*([^*]+)\*)/);

    if (mathMatch) {
      tokens.push({ type: 'math', val: cleanMathText(mathMatch[2]) });
      remaining = remaining.slice(mathMatch[1].length);
    } else if (codeMatch) {
      tokens.push({ type: 'code', val: codeMatch[2] });
      remaining = remaining.slice(codeMatch[1].length);
    } else if (boldMatch) {
      tokens.push({ type: 'bold', val: boldMatch[2] });
      remaining = remaining.slice(boldMatch[1].length);
    } else if (italicMatch) {
      tokens.push({ type: 'italic', val: italicMatch[2] });
      remaining = remaining.slice(italicMatch[1].length);
    } else {
      const nextDollar = remaining.indexOf('$');
      const nextTick = remaining.indexOf('`');
      const nextBold = remaining.indexOf('**');
      const nextItalic = remaining.indexOf('*');

      const nextIndices = [nextDollar, nextTick, nextBold, nextItalic].filter((i) => i >= 0);
      const nextSpecial = nextIndices.length > 0 ? Math.min(...nextIndices) : -1;

      if (nextSpecial === -1) {
        tokens.push({ type: 'text', val: cleanMathText(remaining) });
        remaining = '';
      } else {
        const plain = remaining.slice(0, nextSpecial);
        if (plain) {
          tokens.push({ type: 'text', val: cleanMathText(plain) });
        }
        remaining = remaining.slice(nextSpecial);
      }
    }
  }

  return tokens;
}

function renderInlineTokens(tokens: InlineToken[]) {
  return tokens.map((token, tokenIdx) => {
    if (token.type === 'math') {
      return (
        <span
          key={tokenIdx}
          className="font-mono text-white font-semibold bg-neutral-900/90 px-1.5 py-0.5 rounded mx-0.5 text-[12px] border border-neutral-800 tracking-tight inline-block"
        >
          {token.val}
        </span>
      );
    }
    if (token.type === 'code') {
      return (
        <code
          key={tokenIdx}
          className="font-mono text-white bg-neutral-900 px-1.5 py-0.5 rounded mx-0.5 text-[11px] border border-neutral-800 inline-block font-semibold"
        >
          {token.val}
        </code>
      );
    }
    if (token.type === 'bold') {
      return (
        <strong key={tokenIdx} className="font-bold text-white">
          {token.val}
        </strong>
      );
    }
    if (token.type === 'italic') {
      return (
        <em key={tokenIdx} className="italic text-neutral-300">
          {token.val}
        </em>
      );
    }
    return <span key={tokenIdx}>{token.val}</span>;
  });
}

export default function FormattedContent({
  content,
  className = '',
  isMonoBlock = false
}: FormattedContentProps) {
  if (!content) return null;

  // Pre-split blocks by fenced code blocks
  const blocks: Array<{ type: 'code' | 'text'; content: string; lang?: string }> = [];
  const lines = content.split('\n');

  let inCodeFence = false;
  let codeFenceLang = '';
  let codeFenceBuffer: string[] = [];
  let textBuffer: string[] = [];

  const flushTextBuffer = () => {
    if (textBuffer.length > 0) {
      blocks.push({ type: 'text', content: textBuffer.join('\n') });
      textBuffer = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const fenceMatch = line.match(/^```([a-zA-Z0-9_\-]+)?$/);

    if (fenceMatch) {
      if (!inCodeFence) {
        flushTextBuffer();
        inCodeFence = true;
        codeFenceLang = fenceMatch[1] || '';
        codeFenceBuffer = [];
      } else {
        inCodeFence = false;
        blocks.push({
          type: 'code',
          content: codeFenceBuffer.join('\n'),
          lang: codeFenceLang
        });
        codeFenceBuffer = [];
      }
      continue;
    }

    if (inCodeFence) {
      codeFenceBuffer.push(line);
    } else {
      textBuffer.push(line);
    }
  }

  flushTextBuffer();
  if (inCodeFence && codeFenceBuffer.length > 0) {
    blocks.push({
      type: 'code',
      content: codeFenceBuffer.join('\n'),
      lang: codeFenceLang
    });
  }

  return (
    <div className={`space-y-2 text-neutral-300 leading-relaxed ${className}`}>
      {blocks.map((block, bIdx) => {
        if (block.type === 'code') {
          return (
            <div key={bIdx} className="my-2.5 rounded-lg bg-black border border-neutral-800 overflow-hidden font-mono text-[11px]">
              {block.lang && (
                <div className="px-3 py-1 bg-neutral-900 border-b border-neutral-800 text-[10px] text-neutral-400 uppercase font-semibold">
                  {block.lang}
                </div>
              )}
              <pre className="p-3 text-neutral-200 overflow-x-auto whitespace-pre leading-relaxed">
                <code>{block.content}</code>
              </pre>
            </div>
          );
        }

        const blockLines = block.content.split('\n');
        return (
          <div key={bIdx} className="space-y-1.5">
            {blockLines.map((line, lIdx) => {
              const trimmed = line.trim();
              if (!trimmed) {
                return <div key={lIdx} className="h-1.5" />;
              }

              // Headers
              const h3Match = trimmed.match(/^###\s+(.*)$/);
              if (h3Match) {
                return (
                  <h4 key={lIdx} className="text-xs font-bold text-white pt-2 pb-0.5 tracking-tight uppercase font-mono">
                    {renderInlineTokens(parseInline(h3Match[1]))}
                  </h4>
                );
              }

              const h2Match = trimmed.match(/^##\s+(.*)$/);
              if (h2Match) {
                return (
                  <h3 key={lIdx} className="text-sm font-bold text-white pt-2.5 pb-1 border-b border-neutral-800">
                    {renderInlineTokens(parseInline(h2Match[1]))}
                  </h3>
                );
              }

              // Numbered List (e.g., "1. ")
              const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
              if (numMatch) {
                return (
                  <div key={lIdx} className="flex items-start space-x-2 pl-1 text-xs">
                    <span className="text-neutral-500 font-mono font-bold shrink-0">{numMatch[1]}.</span>
                    <div className="flex-1 text-neutral-200">
                      {renderInlineTokens(parseInline(numMatch[2]))}
                    </div>
                  </div>
                );
              }

              // Bullet List (e.g., "- " or "* ")
              const bulletMatch = trimmed.match(/^[-*•]\s+(.*)$/);
              if (bulletMatch) {
                return (
                  <div key={lIdx} className="flex items-start space-x-2 pl-2 text-xs">
                    <span className="text-white shrink-0 font-bold">•</span>
                    <div className="flex-1 text-neutral-200">
                      {renderInlineTokens(parseInline(bulletMatch[1]))}
                    </div>
                  </div>
                );
              }

              // Normal line
              return (
                <p key={lIdx} className={isMonoBlock ? 'font-mono text-xs' : 'text-xs'}>
                  {renderInlineTokens(parseInline(line))}
                </p>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
