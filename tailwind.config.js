/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#0A0A0A",
        "primary-hover": "#111111",
        "background-light": "#000000",
        "background-dark": "#000000",
        "surface-light": "#0A0A0A",
        "surface-dark": "#0A0A0A",
        "text-main-light": "#E5E5E5",
        "text-main-dark": "#F5F5F5",
        "text-muted-light": "#999999",
        "text-muted-dark": "#777777",
        "border-light": "#0A0A0A",
        "border-dark": "#0A0A0A",
      },
      fontFamily: {
        display: ["'Plus Jakarta Sans'", "sans-serif"],
        body: ["'Plus Jakarta Sans'", "sans-serif"],
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.05)',
        'hover': '0 20px 40px -10px rgba(0, 0, 0, 0.08)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/container-queries'),
  ],
}
