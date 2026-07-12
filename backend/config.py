import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"

for d in (UPLOAD_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---- Gemini ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# gemini-2.5-flash is multimodal (video + audio), stable, and cheap for this workload.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-flash-lite-latest")

DATABASE_URL = f"sqlite:///{DATA_DIR / 'studio.db'}"

STYLES = ["formal", "sarcastic", "humorous_tech", "humorous_non_tech"]
STYLE_LABELS = {
    "formal": "Formal",
    "sarcastic": "Sarcastic",
    "humorous_tech": "Humorous-Tech",
    "humorous_non_tech": "Humorous-Non-Tech",
}
STYLE_DESCRIPTIONS = {
    "formal": "Clear, objective, professional wording.",
    "sarcastic": "Witty, ironic, dry sarcastic commentary.",
    "humorous_tech": (
        "Geeky, developer-culture humor — lean on programmer/tech in-jokes "
        "(bugs, debugging, code reviews, deployments, Stack Overflow, coffee-fueled "
        "coding, jargon like 'it works on my machine'). Punchy one-liners over "
        "puns; the joke should land even without visual context."
    ),
    "humorous_non_tech": "Light, broadly accessible humor for a general audience.",
}