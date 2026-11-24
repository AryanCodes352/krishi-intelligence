/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        krishi: {
          green: {
            dark: '#1a3a2a',
            DEFAULT: '#2d6a4f',
            light: '#52b788',
          },
          gold: {
            DEFAULT: '#d4a017',
            light: '#f4c542',
          },
          soil: '#8b5a2b',
          sky: '#2563eb',
          cream: '#faf7f2',
          white: '#ffffff',
        },
        risk: {
          high: '#dc2626',
          medium: '#f59e0b',
          low: '#16a34a',
        }
      },
      fontFamily: {
        serif: ['var(--font-playfair)', 'Georgia', 'serif'],
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
};
