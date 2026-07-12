import traceback
from pathlib import Path
from database import get_session
from models import VideoJob
from gemini_client import GeminiClient
import media
from config import OUTPUT_DIR
from combined_styles import resolve_tone, pick_color


def _update(session, job, **kwargs):
    for k, v in kwargs.items():
        setattr(job, k, v)
    session.commit()


def run_pipeline(job_uuid: str):
    session = get_session()
    job = session.query(VideoJob).filter_by(job_uuid=job_uuid).first()
    if not job:
        return
    try:
        _update(session, job, status="processing", progress="Starting…")
        video_path = Path(job.stored_path)
        selected_styles = job.get("selected_styles")
        personalization_prompt = job.personalize_prompt or ""

        # Split the video into fixed 7s windows so captions can change over time.
        duration = media.get_duration(video_path)
        windows = media.make_windows(duration)

        tone_name, tone_description = resolve_tone(selected_styles)

        # STEPS 2-8 — Gemini reads audio + visuals, returns everything
        _update(session, job, progress="Analyzing video with Gemini")
        gemini = GeminiClient()
        result = gemini.analyze_video_single(
            video_path, windows, tone_name, tone_description, personalization_prompt
        )

        # Pair the caption list with its time window -> {start, end, text}
        segments = [
            {"start": start, "end": end, "text": result.captions[i] if i < len(result.captions) else ""}
            for i, (start, end) in enumerate(windows)
        ]

        _update(session, job, transcript=result.transcript,
                visual_summary=result.visual_description, summary=result.summary)
        job.set("captions", segments)
        session.commit()

        # STEP 9 — burn the styled video (ffmpeg still needed for this)
        _update(session, job, progress="Rendering video")
        out_path = OUTPUT_DIR / f"{job_uuid}.mp4"
        color = pick_color(selected_styles)
        media.burn_caption(video_path, segments, color, out_path)
        job.output_file = out_path.name
        _update(session, job, status="done", progress="Complete")

    except Exception as e:
        _update(session, job, status="error",
                error=f"{e}\n{traceback.format_exc()}", progress="Failed")
    finally:
        session.close()
