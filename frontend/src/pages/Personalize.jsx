import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { generateCaptions, getCombinedStyles } from "../api";

const STYLE_ORDER = ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"];
const STYLE_CLASS = {
  formal: "formal",
  sarcastic: "sarcastic",
  humorous_tech: "humtech",
  humorous_non_tech: "humnon",
};
const PROMPT_MAX = 50;

function canonicalKey(styles) {
  return [...styles].sort().join("+");
}

export default function Personalize() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const [prompt, setPrompt] = useState("");
  const [selected, setSelected] = useState([]);
  const [meta, setMeta] = useState(null); // { styles, combinations }
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getCombinedStyles().then(setMeta).catch(() => setError("Couldn't load style info."));
  }, []);

  function toggleStyle(key) {
    setSelected((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  }

  const preview = useMemo(() => {
    if (!meta || selected.length === 0) return null;
    if (selected.length === 1) {
      const key = selected[0];
      return {
        mode: "single",
        label: meta.styles[key]?.label || key,
        description: meta.styles[key]?.description || "",
      };
    }
    const combo = meta.combinations[canonicalKey(selected)];
    return {
      mode: "combined",
      labels: selected.map((k) => meta.styles[k]?.label || k),
      name: combo?.name || "Custom Blend",
      description: combo?.description || "A mix of the selected tones.",
    };
  }, [meta, selected]);

  const canGenerate = prompt.trim().length > 0 && selected.length > 0 && !busy;

  async function handleGenerate() {
    if (!canGenerate) return;
    setBusy(true);
    setError("");
    try {
      await generateCaptions(jobId, selected, prompt.trim());
      navigate(`/output/${jobId}`);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  }

  return (
    <div className="personalize">
      <h2>Personalize your captions</h2>

      <div className="field">
        <span className="tag">Prompt</span>
        <textarea
          className="prompt-box"
          placeholder="Enter your prompt here..."
          value={prompt}
          maxLength={PROMPT_MAX}
          onChange={(e) => setPrompt(e.target.value.slice(0, PROMPT_MAX))}
          rows={3}
        />
        <div className="char-counter">
          {prompt.length}/{PROMPT_MAX}
        </div>
      </div>

      <div className="field">
        <span className="tag">Caption style(s)</span>
        <p className="hint">You can select multiple styles to blend their tones.</p>
        <div className="style-grid">
          {STYLE_ORDER.map((key) => (
            <button
              key={key}
              type="button"
              className={`style-btn ${STYLE_CLASS[key]} ${selected.includes(key) ? "active" : ""}`}
              onClick={() => toggleStyle(key)}
            >
              {meta?.styles[key]?.label || key}
            </button>
          ))}
        </div>
      </div>

      {preview && preview.mode === "single" && (
        <div className="preview-card">
          <span className="tag">Selected Style</span>
          <p className="preview-name">{preview.label}</p>
          <p className="preview-desc">{preview.description}</p>
        </div>
      )}

      {preview && preview.mode === "combined" && (
        <div className="preview-card">
          <span className="tag">Selected Styles</span>
          <p className="preview-name">{preview.labels.join(" + ")}</p>
          <span className="tag">Combined Style</span>
          <p className="preview-name">{preview.name}</p>
          <span className="tag">Description</span>
          <p className="preview-desc">{preview.description}</p>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      <button
        className="btn primary generate-btn"
        disabled={!canGenerate}
        onClick={handleGenerate}
      >
        {busy ? "Starting…" : "Generate"}
      </button>
    </div>
  );
}
