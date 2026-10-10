import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) {
    return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

export function getDifficultyColor(difficulty: string): { bg: string; text: string; border: string } {
  switch (difficulty?.toUpperCase()) {
    case "EASY":
      return { bg: "bg-neutral-900", text: "text-neutral-300", border: "border-neutral-700" };
    case "MEDIUM":
      return { bg: "bg-neutral-900", text: "text-white", border: "border-neutral-500" };
    case "HARD":
      return { bg: "bg-white", text: "text-black", border: "border-white" };
    default:
      return { bg: "bg-neutral-950", text: "text-neutral-400", border: "border-neutral-800" };
  }
}
