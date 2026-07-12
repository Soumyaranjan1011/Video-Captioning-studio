import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { uploadVideo } from "../api";

export default function Home() {
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef();
  const navigate = useNavigate();

  async function handleFile(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".mp4")) {
      setError("Please choose an MP4 file.");
      return;
    }
    setError("");
    setBusy(true);
    try {
      const { job_uuid } = await uploadVideo(file);
      navigate(`/select/${job_uuid}`);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  }

  return (
    <div className="home">
      <h1>Turn any video into captioned stories</h1>
      <p className="subtitle">
        Gemini analyzes the audio <em>and</em> visuals, then writes Formal,
        Sarcastic, Humorous-Tech, and Humorous-Non-Tech captions.
      </p>

      <div
        className={`dropzone ${dragging ? "dragging" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFile(e.dataTransfer.files[0]);
        }}
        onClick={() => inputRef.current.click()}
      >
        {busy ? (
          <p>Uploading…</p>
        ) : (
          <>
            <div className="drop-icon">⬆️</div>
            <p><strong>Drag & drop</strong> an MP4 here</p>
            <p className="or">or</p>
            <button className="btn primary" type="button">Upload Video</button>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="video/mp4"
          hidden
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  );
}