import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        panel: "#ffffff",
        line: "#d8e2f0",
        mist: "#eff4fb",
        navy: "#112240",
        accent: "#0f766e",
        sand: "#f7f1e7",
        warn: "#b45309",
        danger: "#b91c1c"
      },
      boxShadow: {
        panel: "0 18px 50px rgba(15, 23, 42, 0.08)"
      },
      backgroundImage: {
        "studio-glow":
          "radial-gradient(circle at top left, rgba(15,118,110,0.18), transparent 28%), radial-gradient(circle at top right, rgba(17,34,64,0.15), transparent 32%), linear-gradient(180deg, #f8fafc 0%, #eef3f9 100%)"
      }
    }
  },
  plugins: []
};

export default config;

