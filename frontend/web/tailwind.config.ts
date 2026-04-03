import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        compliance: {
          bg: '#0B1020',
          card: '#121A2D',
          accent: '#4F46E5',
          ok: '#22C55E',
          warn: '#F59E0B',
          fail: '#EF4444'
        }
      }
    }
  },
  plugins: []
};

export default config;
