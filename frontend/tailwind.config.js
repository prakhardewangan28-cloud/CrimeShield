/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cs: {
          bg: '#080D18',
          sidebar: '#0D1422',
          card: '#111C2D',
          cardHover: '#162338',
          border: '#1E293B',
          borderLight: '#334155',
          cyan: '#22D3EE',
          blue: '#3B82F6',
          violet: '#8B5CF6',
          text: '#F1F5F9',
          muted: '#94A3B8',
          success: '#22C55E',
          warning: '#F59E0B',
          error: '#EF4444'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      boxShadow: {
        'glow-cyan': '0 0 20px -5px rgba(34, 211, 238, 0.3)',
        'glow-blue': '0 0 20px -5px rgba(59, 130, 246, 0.3)',
        'glow-violet': '0 0 20px -5px rgba(139, 92, 246, 0.3)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.5)'
      }
    },
  },
  plugins: [],
}
