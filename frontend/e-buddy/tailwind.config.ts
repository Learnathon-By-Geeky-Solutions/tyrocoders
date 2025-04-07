import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "15px",
    },
    screens: {
      sm: "640px",
      md: "768px",
      lg: "960px",
      xl: "1200px",
    },
    fontFamily: {
      primary: "var(--font-jetbrainsMono)",
    },
    extend: {
      colors: {
        primary: "#222629",
        accent: {
          DEFAULT: "#97d343",
          hover: "#86c232",
        },
        chatbot: {
          primary: "#9b87f5",
          secondary: "#7E69AB",
          light: "#E5DEFF",
          dark: "#1A1F2C",
          bubble: {
            user: "#F1F0FB",
            bot: "#D6BCFA",
          },
        },
        bot: {
          primary: "#6366f1",
          secondary: "#4f46e5",
          accent: "#818cf8",
          background: "#f5f7ff",
          surface: "#ffffff",
          success: "#10b981",
          highlight: "#dbeafe",
        },
        secondary: "#474b4f",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-in": {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        typing: {
          "0%": { width: "0%" },
          "100%": { width: "100%" },
        },
        "pulse-subtle": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.85" },
        },
      },
      animation: {
        "accordion-up": "accordion-up 0.2s ease-out",
        "accordion-down": "accordion-down 0.2s ease-out",
        "fade-in": "fade-in 0.3s ease-out",
        "slide-in": "slide-in 0.3s ease-out",
        typing: "typing 1.5s steps(40, end)",
        "pulse-subtle": "pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      boxShadow: {
        "bot-card":
          "0 10px 25px -5px rgba(99, 102, 241, 0.1), 0 8px 10px -6px rgba(99, 102, 241, 0.05)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
