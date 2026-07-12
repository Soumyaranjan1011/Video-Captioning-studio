import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { generateCaptions } from "../api";

const STYLES = [
  { key: "formal", label: "Formal", cls: "formal" },
  { key: "sarcastic", label: "Sarcastic", cls: "sarcastic" },
  { key: "humorous_tech", label: "Humorous-Tech", cls: "humtech" },
  { key: "humorous_non_tech", label: "Humorous-Non-Tech", cls: "humnon" },
];

export default function StyleSelect() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [busyStyle, setBusyStyle] = useState(null);
  const [error, setError] = useState("");

  async function pick(key) {
    setError("");
    setBusyStyle(key);
    try {
      await generateCaptions(jobId, [key]);
      navigate(`/output/${jobId}`);
    } catch (e) {
      setError(e.message);
      setBusyStyle(null);
    }
  }

  return (
    <div className="style-select">
      <h2>Choose a caption style</h2>
      <p className="subtitle">
        Pick one style to generate captions in that tone, or personalize your
        own blend.
      </p>

      <div className="style-grid">
        {STYLES.map(({ key, label, cls }) => (
          <button
            key={key}
            className={`style-btn ${cls}`}
            disabled={busyStyle !== null}
            onClick={() => pick(key)}
          >
            {busyStyle === key ? "Starting…" : label}
          </button>
        ))}
        <button
          className="style-btn personalize"
          disabled={busyStyle !== null}
          onClick={() => navigate(`/personalize/${jobId}`)}
        >
          ✨ Personalize
        </button>
      </div>

      {error && <p className="error">{error}</p>}
    </div>
  );
}
