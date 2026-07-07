/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#FFF8ED",
          100: "#FFEFD0",
          200: "#FFD99A",
          300: "#FFBC5E",
          400: "#FF9D2A",
          500: "#F5A623",
          600: "#C4821A",
          700: "#9A6110",
          800: "#7A4D0D",
          900: "#5C3A0A",
        },
      },
      fontFamily: {
        display: ["'Syne'", "sans-serif"],
        body: ["'DM Sans'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
