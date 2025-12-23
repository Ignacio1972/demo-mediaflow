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
        // OPCIÓN 4: Nexus Style (inspirado en Nexus Dashboard)
        nexus: {
          "primary": "#3b82f6",       // Blue 500
          "primary-content": "#ffffff",
          "secondary": "#6366f1",     // Indigo 500
          "secondary-content": "#ffffff",
          "accent": "#8b5cf6",        // Violet 500
          "accent-content": "#ffffff",
          "neutral": "#1f2937",       // Gray 800
          "neutral-content": "#f9fafb",
          "base-100": "#ffffff",      // Pure white
          "base-200": "#f8fafc",      // Slate 50 (slightly warmer)
          "base-300": "#cbd5e1",      // Slate 300 (visible borders)
          "base-content": "#1f2937",  // Gray 800
          "info": "#0ea5e9",          // Sky 500
          "info-content": "#ffffff",
          "success": "#10b981",       // Emerald 500
          "success-content": "#ffffff",
          "warning": "#f59e0b",       // Amber 500
          "warning-content": "#ffffff",
          "error": "#ef4444",         // Red 500
          "error-content": "#ffffff",
          // Refined styling
          "--rounded-box": "0.75rem",
          "--rounded-btn": "0.5rem",
          "--rounded-badge": "0.5rem",
          "--border-btn": "1px",
          "--tab-radius": "0.5rem",
        },
        // OPCIÓN 5: HRM (basado en Caramellatte de DaisyUI 5)
        hrm: {
          "primary": "#000000",      // Negro puro
          "primary-content": "#ffffff",
          "secondary": "#3d2317",    // Marrón oscuro cálido
          "secondary-content": "#e8ceb0",
          "accent": "#c96f5a",       // Terracota (botón Details)
          "accent-content": "#ffffff",
          "neutral": "#7c4a2d",      // Marrón chocolate
          "neutral-content": "#fcf6ed",
          "base-100": "#fcf6ed",     // Crema muy claro
          "base-200": "#f5e6d3",     // Beige claro
          "base-300": "#e8ceb0",     // Caramelo claro (bordes)
          "base-content": "#7c4a2d", // Marrón chocolate
          "info": "#2563eb",
          "info-content": "#ffffff",
          "success": "#059669",
          "success-content": "#ffffff",
          "warning": "#fbbf24",
          "warning-content": "#78350f",
          "error": "#dc2626",
          "error-content": "#ffffff",
          // Styling
          "--rounded-box": "1rem",
          "--rounded-btn": "2rem",
          "--rounded-badge": "2rem",
          "--border-btn": "2px",
        },
      },
      // All 35 DaisyUI built-in themes
      "light", "dark", "cupcake", "bumblebee", "emerald", "corporate",
      "synthwave", "retro", "cyberpunk", "valentine", "halloween",
      "garden", "forest", "aqua", "lofi", "pastel", "fantasy",
      "wireframe", "black", "luxury", "dracula", "cmyk", "autumn",
      "business", "acid", "lemonade", "night", "coffee", "winter",
      "dim", "nord", "sunset",
    ],
    darkTheme: "mediaflow",  // Cambiar a: mediaflow | cleanwhite | nordic
    base: true,
    styled: true,
    utils: true,
  },
}
