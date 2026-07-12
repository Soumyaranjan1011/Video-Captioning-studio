import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getArchive } from "../api";

const STYLE_LABELS = {
  formal: "Formal",
  sarcastic: "Sarcastic",
  humorous_tech: "Humorous-Tech",
  humorous_non_tech: "Humorous-Non-Tech",
};

const THUMB_SECONDS = 5;

function handleThumbTimeUpdate(e) {
  if (e.target.currentTime >= THUMB_SECONDS) {
    e.target.currentTime = 0;
  }
}

export default function Archive() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => { getArchive().then(setJobs); }, []);

  return (
    <div className="archive">
      <h2>History</h2>
      {jobs.length === 0 && <p>No uploads yet.</p>}
      {jobs.map((job) => {
        const styles = job.selected_styles || [];
        const styleLabel = styles.map((k) => STYLE_LABELS[k] || k).join(" + ");
        const preview = (job.captions || []).map((s) => s.text).filter(Boolean).join(" ");
        const target = job.status === "uploaded" ? `/select/${job.job_uuid}` : `/output/${job.job_uuid}`;
        const hasVideo = job.status === "done";

        return (
          <div key={job.job_uuid} className="archive-entry">
            <div className="archive-head">
              <div>
                <strong>{job.original_name}</strong>
                <span className="date">
                  {new Date(job.upload_date).toLocaleString()}
                </span>
              </div>
              <span className={`status ${job.status}`}>{job.status}</span>
            </div>

            {styles.length > 0 && (
              <div className="archive-row">
                {hasVideo ? (
                  <video
                    className="archive-thumb"
                    src={`/api/video/${job.job_uuid}`}
                    muted
                    autoPlay
                    loop
                    playsInline
                    onTimeUpdate={handleThumbTimeUpdate}
                  />
                ) : (
                  <div className="archive-thumb archive-thumb-placeholder">🎬</div>
                )}
                <div className="archive-details">
                  <span className="chip generic">
                    {job.combined_style_name || styleLabel}
                  </span>
                  {preview && <p className="cap">{preview}</p>}
                  {job.summary && <p className="sum">{job.summary}</p>}
                </div>
              </div>
            )}

            <Link className="view-link" to={target}>
              Open →
            </Link>
          </div>
        );
      })}
    </div>
  );
}
