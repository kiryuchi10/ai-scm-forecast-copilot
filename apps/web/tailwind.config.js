/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: "#f59e0b",
          muted: "#b45309",
          light: "#fbbf24",
        },
      },
    },
  },
  plugins: [],
};
