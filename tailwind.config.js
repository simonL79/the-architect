/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0e0e10',
        accent: '#00ffe1',
        panel: 'rgba(255,255,255,0.04)',
      },
      fontFamily: {
        mono: ['SF Mono', 'Roboto Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
