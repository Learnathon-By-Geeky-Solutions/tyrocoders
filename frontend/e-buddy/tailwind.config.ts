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
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // primary: "#191E27",
        // accent: {
        //   DEFAULT: "#97d343",
        //   hover: "#86c232",
        // },
        chatbot: {
          primary: "#9b87f5",
          secondary: "#7E69AB",
          blue: "#1EAEDB",
          purple: "#9b87f5",
          orange: "#F97316",
          pink: "#D946EF",
          lightBlue: "#33C3F0",
          light: "#E5DEFF",
          dark: "#1A1F2C",
          bubble: {
            user: "#F1F0FB",
            bot: "#D6BCFA",
          },
        },
        // vibrant: "#8B5CF6",
        vibrant: "#ED6140",
        bot: {
          primary: "#6366f1",
          secondary: "#4f46e5",
          accent: "#818cf8",
          background: "#f5f7ff",
          surface: "#ffffff",
          success: "#10b981",
          highlight: "#dbeafe",
        },
        // secondary: "#474b4f",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      scale: {
        "102": "1.02",
        "103": "1.03",
        "104": "1.04",
      },
      keyframes: {
        "fade-in": {
          "0%": {
            opacity: "0",
          },
          "100%": {
            opacity: "1",
          },
        },
        "slide-in": {
          "0%": {
            transform: "translateY(10px)",
            opacity: "0",
          },
          "100%": {
            transform: "translateY(0)",
            opacity: "1",
          },
        },
        typing: {
          "0%": {
            width: "0%",
          },
          "100%": {
            width: "100%",
          },
        },
        "pulse-subtle": {
          "0%, 100%": {
            opacity: "1",
          },
          "50%": {
            opacity: "0.85",
          },
        },
        "accordion-down": {
          from: {
            height: "0",
          },
          to: {
            height: "var(--radix-accordion-content-height)",
          },
        },
        "accordion-up": {
          from: {
            height: "var(--radix-accordion-content-height)",
          },
          to: {
            height: "0",
          },
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
