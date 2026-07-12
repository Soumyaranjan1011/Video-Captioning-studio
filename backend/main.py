import uuid
import shutil
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import UPLOAD_DIR, OUTPUT_DIR, STYLES, STYLE_LABELS, STYLE_DESCRIPTIONS
from database import init_db, get_session
from models import VideoJob
from pipeline import run_pipeline
from combined_styles import COMBINED_STYLES, get_combined_style

app = FastAPI(title="Video Captioning Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class GenerateRequest(BaseModel):
    styles: List[str]
    prompt: str = Field(default="", max_length=50)


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(400, "Please upload an MP4 file.")

    job_uuid = uuid.uuid4().hex
    stored = UPLOAD_DIR / f"{job_uuid}.mp4"
    with stored.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    session = get_session()
    job = VideoJob(job_uuid=job_uuid, original_name=file.filename,
                   stored_path=str(stored), status="uploaded")
    session.add(job)
    session.commit()
    session.close()

    # Generation is deferred until the user picks a style on the next page.
    return {"job_uuid": job_uuid}


@app.get("/api/combined-styles")
def combined_styles():
    """Static mapping the Personalize page uses for instant, offline preview
    of what tone results from a given set of selected base styles."""
    return {
        "styles": {
            key: {"label": STYLE_LABELS[key], "description": STYLE_DESCRIPTIONS[key]}
            for key in STYLES
        },
        "combinations": COMBINED_STYLES,
    }


@app.post("/api/generate/{job_uuid}")
def generate(job_uuid: str, req: GenerateRequest, background_tasks: BackgroundTasks):
    if not req.styles:
        raise HTTPException(400, "Select at least one style.")
    invalid = [s for s in req.styles if s not in STYLES]
    if invalid:
        raise HTTPException(400, f"Unknown style(s): {', '.join(invalid)}")

    session = get_session()
    job = session.query(VideoJob).filter_by(job_uuid=job_uuid).first()
    if not job:
        session.close()
        raise HTTPException(404, "Job not found.")

    job.set("selected_styles", req.styles)
    job.personalize_prompt = req.prompt.strip()
    if len(req.styles) > 1:
        combo = get_combined_style(req.styles)
        job.combined_style_name = combo["name"] if combo else ""
        job.combined_style_description = combo["description"] if combo else ""
    else:
        job.combined_style_name = ""
        job.combined_style_description = ""
    job.status = "queued"
    job.progress = "Queued"
    session.commit()
    session.close()

    background_tasks.add_task(run_pipeline, job_uuid)
    return {"job_uuid": job_uuid}


@app.get("/api/status/{job_uuid}")
def status(job_uuid: str):
    session = get_session()
    job = session.query(VideoJob).filter_by(job_uuid=job_uuid).first()
    session.close()
    if not job:
        raise HTTPException(404, "Job not found.")
    return job.to_dict()


@app.get("/api/archive")
def archive():
    session = get_session()
    jobs = session.query(VideoJob).order_by(VideoJob.upload_date.desc()).all()
    data = [j.to_dict() for j in jobs]
    session.close()
    return data


@app.get("/api/original/{job_uuid}")
def original(job_uuid: str):
    path = UPLOAD_DIR / f"{job_uuid}.mp4"
    if not path.exists():
        raise HTTPException(404, "Not found.")
    return FileResponse(path, media_type="video/mp4")


@app.get("/api/video/{job_uuid}")
def download(job_uuid: str):
    path = OUTPUT_DIR / f"{job_uuid}.mp4"
    if not path.exists():
        raise HTTPException(404, "Video not ready.")
    return FileResponse(path, media_type="video/mp4",
                        filename=f"{job_uuid}.mp4")


# Serves the built React app when running inside Docker (frontend/dist is
# copied to backend/static during the image build). Inactive in local dev,
# where the Vite dev server serves the frontend instead.
FRONTEND_DIST = Path(__file__).resolve().parent / "static"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")
