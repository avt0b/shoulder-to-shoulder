/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#6366f1",
        accent: "#ec4899",
        success: "#10b981",
        warning: "#f59e0b",
        danger: "#ef4444",
      },
      spacing: {
        "safe": "env(safe-area-inset-bottom)",
      },
    },
  },
  plugins: [],
}
