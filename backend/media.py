import subprocess
from pathlib import Path
from typing import List, Tuple

CAPTION_INTERVAL_SECONDS = 7.0

# Caption outline stroke color per style (ASS &HBBGGRR, reversed byte order
# from normal RGB). Keyed directly by style name — "combined" covers any
# Personalize job with 2+ base styles selected.
_ASS_OUTLINE_COLORS = {
    "formal":             "&H00000000",  # black
    "sarcastic":          "&H0058DBFF",  # mustard yellow (#FFDB58)
    "humorous_tech":      "&H008B0000",  # dark blue (#00008B)
    "humorous_non_tech":  "&H00006400",  # dark green (#006400)
    "combined":           "&H00A8216B",  # deep violet-purple (#6B21A8)
}


def _run(cmd):
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print("\n===== FFMPEG STDOUT =====")
    print(result.stdout)

    print("\n===== FFMPEG STDERR =====")
    print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


def get_duration(video_path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True, check=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def make_windows(duration: float, interval: float = CAPTION_INTERVAL_SECONDS) -> List[Tuple[float, float]]:
    """Split [0, duration] into fixed-length windows (last one may be shorter)."""
    if duration <= 0:
        return [(0.0, 0.0)]
    windows = []
    t = 0.0
    while t < duration:
        end = min(t + interval, duration)
        windows.append((round(t, 2), round(end, 2)))
        t += interval
    return windows


def _escape_ass(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def _write_ass(segments: List[dict], color_name: str, ass_path: Path, duration: float):
    """segments: list of {"start": float, "end": float, "text": str}, one
    Dialogue cue per segment so the caption changes over time.

    Clean subtitle look: white text, no background box, thin outline in a
    pastel shade of the target style's color (BorderStyle=1 = stroke, not
    a filled box).
    """
    outline = _ASS_OUTLINE_COLORS.get(color_name, "&H00D9D9D9")
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginV
Style: Main,DejaVu Sans,38,&H00FFFFFF,{outline},0,1,1.3,1,2,40

[Events]
Format: Layer, Start, End, Style, Text
"""

    def ts(sec):
        h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    lines = []
    for seg in segments:
        start = max(0.0, float(seg.get("start", 0.0)))
        end = float(seg.get("end", start))
        if duration:
            end = min(end, duration)
        text = _escape_ass(seg.get("text", ""))
        if end <= start or not text:
            continue
        # Text is the last field in the Events Format above, so no trailing
        # commas here — anything extra gets swallowed into the caption text.
        lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Main,{text}")

    print("WRITING ASS FILE:", ass_path, "-", len(lines), "cues")
    ass_path.write_text(header + "\n".join(lines), encoding="utf-8")
    return ass_path


def burn_caption(video_path: Path, segments: List[dict], color: str, out_path: Path):
    duration = get_duration(video_path)

    ass_path = out_path.with_suffix(".ass")

    _write_ass(segments, color, ass_path, duration)

    ass_file = str(ass_path).replace("\\", "/")
    ass_file = ass_file.replace(":", "\\:")

    _run([
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"ass={ass_file}",
        "-c:a",
        "copy",
        str(out_path)
    ])

    ass_path.unlink(missing_ok=True)

    return out_path