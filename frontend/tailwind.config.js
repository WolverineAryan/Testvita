/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#fafafa",
          100: "#f4f4f5",
          200: "#e4e4e7",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#ffffff", // Pure white
          600: "#f4f4f5",
          700: "#e4e4e7",
          800: "#27272a",
          900: "#18181b",
          950: "#09090b"
        },
        dark: {
          950: "#000000", // Pure black
          900: "#09090b", // Obsidian / Zinc 950
          850: "#121214", // Surface black
          800: "#18181b", // Zinc 900
          750: "#222226", // Border hover
          700: "#27272a", // Standard border
          600: "#3f3f46"  // Muted border
        },
        accent: {
          cyan: "#ffffff",
          emerald: "#e4e4e7",
          amber: "#d4d4d8",
          rose: "#a1a1aa",
          violet: "#ffffff"
        }
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"]
      }
    },
  },
  plugins: [],
};
