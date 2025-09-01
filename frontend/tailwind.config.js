// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Your existing theme extensions
    },
  },
  plugins: [
    // Add this if you don't have it
    require('@tailwindcss/forms'),
  ],
  // Ensure these utilities are not purged
  safelist: [
    'backdrop-blur-xl',
    'backdrop-blur-2xl',
    'backdrop-saturate-150',
  ],
}