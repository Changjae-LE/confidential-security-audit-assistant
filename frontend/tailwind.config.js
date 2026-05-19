/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#162027",
        panel: "#f7f9fb",
        line: "#d7e0e8",
        mint: "#2f8f83",
        amber: "#b7791f",
        danger: "#b42318",
      },
    },
  },
  plugins: [],
};
