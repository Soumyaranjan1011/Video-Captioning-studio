export async function uploadVideo(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/upload", { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
  return res.json();
}

export async function getStatus(jobId) {
  const res = await fetch(`/api/status/${jobId}`);
  return res.json();
}

export async function getArchive() {
  const res = await fetch("/api/archive");
  return res.json();
}

export async function getCombinedStyles() {
  const res = await fetch("/api/combined-styles");
  return res.json();
}

export async function generateCaptions(jobId, styles, prompt = "") {
  const res = await fetch(`/api/generate/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ styles, prompt }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Generate failed");
  return res.json();
}
