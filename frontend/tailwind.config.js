/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        leuphana: "#821A1F", // Leuphana maroon
      },
    },
  },
  plugins: [],
}
