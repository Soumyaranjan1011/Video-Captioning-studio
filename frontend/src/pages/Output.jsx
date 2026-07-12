import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { getStatus } from "../api";

const STYLE_LABELS = {
  formal: "Formal",
  sarcastic: "Sarcastic",
  humorous_tech: "Humorous-Tech",
  humorous_non_tech: "Humorous-Non-Tech",
};

export default function Output() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [fetchError, setFetchError] = useState("");
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    let timer;

    async function poll() {
      try {
        const data = await getStatus(jobId);
        if (!mounted.current) return;
        setJob(data);
        if (data.status !== "done" && data.status !== "error") {
          timer = setTimeout(poll, 2500);
        }
      } catch (e) {
        if (!mounted.current) return;
        setFetchError("Couldn't reach the server. Retrying…");
        timer = setTimeout(poll, 4000);
      }
    }

    poll();
    return () => {
      mounted.current = false;
      clearTimeout(timer);
    };
  }, [jobId]);

  if (fetchError && !job) return <p className="error">{fetchError}</p>;
  if (!job) return <p>Loading…</p>;

  if (job.status === "error") {
    return (
      <div className="results">
        <h2>Something went wrong</h2>
        <pre className="error-box">{job.error}</pre>
      </div>
    );
  }

  const done = job.status === "done";
  const segments = job.captions || [];
  const isCombined = (job.selected_styles || []).length > 1;

  const formatTs = (sec) => {
    const s = Math.max(0, Math.floor(sec || 0));
    const m = Math.floor(s / 60);
    const r = s % 60;
    return `${m}:${String(r).padStart(2, "0")}`;
  };

  return (
    <div className="results">
      <h2>{job.original_name}</h2>

      {!done && (
        <div className="progress-card">
          <div className="spinner" />
          <p>{job.progress || "Working…"}</p>
        </div>
      )}

      <section className="preview">
        <h3>{done ? "Captioned video" : "Original video"}</h3>
        <video
          controls
          src={done ? `/api/video/${jobId}` : `/api/original/${jobId}`}
          className="video"
        />
      </section>

      <div className="info-block">
        {job.personalize_prompt && (
          <div className="field">
            <span className="tag">Personalization Prompt</span>
            <p>{job.personalize_prompt}</p>
          </div>
        )}
        <div className="field">
          <span className="tag">Selected Style{(job.selected_styles || []).length > 1 ? "s" : ""}</span>
          <p>{(job.selected_styles || []).map((k) => STYLE_LABELS[k] || k).join(" + ") || "—"}</p>
        </div>
        {isCombined && job.combined_style_name && (
          <div className="field">
            <span className="tag">Combined Style</span>
            <p>
              <strong>{job.combined_style_name}</strong>
              {job.combined_style_description ? ` — ${job.combined_style_description}` : ""}
            </p>
          </div>
        )}
      </div>

      {done && (
        <div className="output-card">
          <div className="field">
            <span className="tag">Captions (every 7s)</span>
            {segments.length ? (
              <ul className="caption-segments">
                {segments.map((seg, i) => (
                  <li key={i}>
                    <span className="ts">{formatTs(seg.start)}–{formatTs(seg.end)}</span>{" "}
                    {seg.text || "—"}
                  </li>
                ))}
              </ul>
            ) : (
              <p>—</p>
            )}
          </div>
          <div className="field">
            <span className="tag">Summary</span>
            <p>{job.summary || "—"}</p>
          </div>
          <a className="btn download" href={`/api/video/${jobId}`}>
            ⬇ Download video
          </a>
        </div>
      )}
    </div>
  );
}
