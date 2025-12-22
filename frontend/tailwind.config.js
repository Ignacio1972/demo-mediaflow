/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        // OPCIÓN 1: Minimalista Oscuro (Default)
        mediaflow: {
          "primary": "#06b6d4",      // Cyan/Celeste moderno
          "secondary": "#06b6d4",    // Cyan/Celeste
          "accent": "#14b8a6",       // Teal elegante
          "neutral": "#1e293b",      // Slate oscuro
          "base-100": "#0f172a",     // Casi negro
          "base-200": "#1e293b",     // Slate medio
          "base-300": "#334155",     // Slate claro
          "info": "#3b82f6",
          "success": "#10b981",
          "warning": "#f59e0b",
          "error": "#ef4444",
        },
        // OPCIÓN 2: Clean White (Minimalista Claro)
        cleanwhite: {
          "primary": "#06b6d4",      // Cyan/Celeste profesional
          "secondary": "#06b6d4",    // Cyan/Celeste
          "accent": "#0891b2",       // Cyan
          "neutral": "#1f2937",
          "base-100": "#ffffff",     // Blanco puro
          "base-200": "#f8fafc",     // Gris muy claro
          "base-300": "#e2e8f0",     // Gris claro
          "info": "#0ea5e9",
          "success": "#059669",
          "warning": "#d97706",
          "error": "#dc2626",
        },
        // OPCIÓN 3: Nordic Light (Escandinavo)
        nordic: {
          "primary": "#06b6d4",      // Cyan/Celeste
          "secondary": "#06b6d4",    // Cyan claro
          "accent": "#14b8a6",       // Teal
          "neutral": "#475569",
          "base-100": "#f1f5f9",     // Gris clarísimo
          "base-200": "#e2e8f0",     // Gris suave
          "base-300": "#cbd5e1",     // Gris medio
          "info": "#0284c7",
          "success": "#16a34a",
          "warning": "#ca8a04",
          "error": "#dc2626",
        },
      },
      "dark",           // DaisyUI dark theme
      "light",          // DaisyUI light theme
      "cupcake",        // DaisyUI cupcake (pastel)
      "cyberpunk",      // DaisyUI cyberpunk
      "business",       // DaisyUI business (profesional)
      "caramellatte",   // DaisyUI caramellatte (warm light)
    ],
    darkTheme: "mediaflow",  // Cambiar a: mediaflow | cleanwhite | nordic
    base: true,
    styled: true,
    utils: true,
  },
}
