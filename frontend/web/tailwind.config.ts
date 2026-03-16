import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#ddebff',
          500: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a'
        }
      }
    }
  },
  plugins: []
};

export default config;
