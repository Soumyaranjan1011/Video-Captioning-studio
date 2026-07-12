import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import StyleSelect from "./pages/StyleSelect";
import Personalize from "./pages/Personalize";
import Output from "./pages/Output";
import Archive from "./pages/Archive";
import "./styles.css";

function useTheme() {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return [theme, setTheme];
}

function App() {
  const [theme, setTheme] = useTheme();

  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/" className="brand">🎬 Video Captioning Studio</Link>
        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/archive">History</Link>
          <button
            className="theme-toggle"
            onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
            aria-label="Toggle theme"
            title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
        </div>
      </nav>
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/select/:jobId" element={<StyleSelect />} />
          <Route path="/personalize/:jobId" element={<Personalize />} />
          <Route path="/output/:jobId" element={<Output />} />
          <Route path="/archive" element={<Archive />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);