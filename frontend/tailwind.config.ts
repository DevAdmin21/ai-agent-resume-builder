import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        chatBg: '#ffffff',
        userMsg: '#f3f4f6',
        aiMsg: '#ffffff',
        borderLight: '#e5e7eb',
      }
    },
  },
  plugins: [],
} satisfies Config