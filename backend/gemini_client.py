import time
from pathlib import Path
from typing import List, Tuple
from pydantic import BaseModel
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL


class SingleStyleResult(BaseModel):
    """One caption per fixed time window (index i -> window i), for a single
    target tone, plus one overall summary."""
    transcript: str
    visual_description: str
    captions: List[str]
    summary: str


class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def _upload_and_wait(self, video_path: Path, timeout=300):
        """Upload the video and block until Gemini finishes processing it."""
        uploaded = self.client.files.upload(file=str(video_path))
        start = time.time()
        while uploaded.state.name == "PROCESSING":
            if time.time() - start > timeout:
                raise TimeoutError("Gemini took too long to process the video.")
            time.sleep(3)
            uploaded = self.client.files.get(name=uploaded.name)
        if uploaded.state.name == "FAILED":
            raise RuntimeError("Gemini failed to process the video.")
        return uploaded

    def analyze_video_single(
        self,
        video_path: Path,
        windows: List[Tuple[float, float]],
        tone_name: str,
        tone_description: str,
        personalization_prompt: str = "",
    ) -> SingleStyleResult:
        """One call: Gemini reads audio + visuals and returns transcript,
        visual description, one caption per fixed time window for the given
        target tone, and one overall summary."""
        video_file = self._upload_and_wait(video_path)

        window_lines = "\n".join(
            f"Window {i + 1}: {start:.1f}s - {end:.1f}s"
            for i, (start, end) in enumerate(windows)
        )

        personalization_block = ""
        if personalization_prompt.strip():
            personalization_block = f"""
The user has also given this personalization instruction — factor it into
the captions' focus/content wherever relevant, without breaking the target
tone above:
"{personalization_prompt.strip()}"
"""

        system = "You are an expert video caption creator."
        prompt = f"""Analyze this video using BOTH its audio (spoken content) and its visuals.

First, internally note:
- A transcript of the spoken content (empty string if no clear speech).
- A short visual description of what happens on screen.

The video is split into these fixed, consecutive time windows:
{window_lines}

Generate exactly one caption PER WINDOW (same number of captions as windows
listed above, in the same order). Each window's caption must describe/reflect
ONLY what is said and shown specifically during that window's time range —
not the whole video. Consecutive windows should read like a running
commentary that changes as the video's audio/visual content changes; do not
reuse an identical caption across windows unless the content genuinely
repeats.

TARGET TONE: {tone_name}
Tone guidance: {tone_description}
{personalization_block}
CAPTION requirements (per window) — PRIORITY: audio over visuals:
- If the window has ANY clear spoken content, the caption MUST be built
  primarily around what is actually said — apply the target tone/humor to
  the speech itself (e.g. a witty/funny spin on the words spoken). Visuals
  may only add brief secondary color in this case; they must never replace
  or outweigh the spoken content as the caption's main subject.
- Only when a window has NO clear speech at all (e.g. only background music,
  ambient sound, or silence) should the caption instead be based entirely on
  what is visually happening on screen.
- Maximum 10 words per caption (windows are short, keep it tight)
- Consistently written in the target tone above

SUMMARY requirement (whole video, one summary):
- Maximum 2 sentences
- Match the target tone above

Return everything in the required structured format. The captions list must
have exactly {len(windows)} entries."""

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[video_file, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.8,
                response_mime_type="application/json",
                response_schema=SingleStyleResult,
            ),
        )

        # Clean up the uploaded file server-side.
        try:
            self.client.files.delete(name=video_file.name)
        except Exception:
            pass

        return response.parsed  # already a SingleStyleResult instance