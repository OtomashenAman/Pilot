import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0b1020",
        card: "#121a2b",
        muted: "#98a2b3",
        accent: "#36cfc9",
        danger: "#ff6b6b",
        success: "#52c41a"
      }
    }
  },
  plugins: []
};

export default config;
