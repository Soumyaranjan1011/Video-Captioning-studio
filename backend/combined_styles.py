"""Maps combinations of 2+ base caption styles to a single blended tone
(name + description). Used by the Personalize feature so multiple selected
styles resolve to one coherent tone instead of stacking four separate ones.

Keyed by a canonical string (sorted style keys joined with "+") so it's
JSON-friendly for the /api/combined-styles endpoint and easy to look up from
the frontend with the same key format.
"""
from typing import List, Optional, Tuple
from config import STYLE_LABELS, STYLE_DESCRIPTIONS

FORMAL = "formal"
SARCASTIC = "sarcastic"
HUM_TECH = "humorous_tech"
HUM_NONTECH = "humorous_non_tech"


def canonical_key(style_keys: List[str]) -> str:
    return "+".join(sorted(style_keys))


COMBINED_STYLES = {
    canonical_key([FORMAL, SARCASTIC]): {
        "name": "Dry Wit",
        "description": "Professional wording with subtle sarcasm and understated humor.",
    },
    canonical_key([FORMAL, HUM_TECH]): {
        "name": "Professional Tech Humor",
        "description": "Polished, precise language with clever technical jokes woven in.",
    },
    canonical_key([FORMAL, HUM_NONTECH]): {
        "name": "Polished Lighthearted",
        "description": "Formal tone softened with warm, general-audience humor.",
    },
    canonical_key([SARCASTIC, HUM_TECH]): {
        "name": "Geeky Satire",
        "description": "Sharp sarcasm aimed at tech culture and jargon.",
    },
    canonical_key([SARCASTIC, HUM_NONTECH]): {
        "name": "Playful Roast",
        "description": "Cheeky, teasing sarcasm with broad comedic appeal.",
    },
    canonical_key([HUM_TECH, HUM_NONTECH]): {
        "name": "Universal Comedy",
        "description": "Humor that lands with both tech and general audiences.",
    },
    canonical_key([FORMAL, SARCASTIC, HUM_TECH]): {
        "name": "Intellectual Dry Comedy",
        "description": "Composed delivery, dry sarcasm, and tech-savvy wit combined.",
    },
    canonical_key([FORMAL, SARCASTIC, HUM_NONTECH]): {
        "name": "Sophisticated Comedy",
        "description": "Refined phrasing carrying sarcastic, broadly funny undertones.",
    },
    canonical_key([SARCASTIC, HUM_TECH, HUM_NONTECH]): {
        "name": "Chaotic Comedy",
        "description": "Unpredictable mashup of sarcasm, tech humor, and mainstream comedy.",
    },
    canonical_key([FORMAL, HUM_TECH, HUM_NONTECH]): {
        "name": "Refined Universal Humor",
        "description": "Professional tone carrying both technical and mainstream comedic beats.",
    },
    canonical_key([FORMAL, SARCASTIC, HUM_TECH, HUM_NONTECH]): {
        "name": "Adaptive Hybrid Style",
        "description": "A blend of all four tones — polished, sarcastic, technical, and broadly comedic.",
    },
}


def get_combined_style(style_keys: List[str]) -> Optional[dict]:
    """Returns {"name", "description"} for 2+ styles, or None for 0-1 styles."""
    if len(style_keys) < 2:
        return None
    return COMBINED_STYLES.get(canonical_key(style_keys))


def resolve_tone(style_keys: List[str]) -> Tuple[str, str]:
    """Returns (tone_name, tone_description) for any 1+ selected base styles."""
    if len(style_keys) == 1:
        key = style_keys[0]
        return STYLE_LABELS[key], STYLE_DESCRIPTIONS[key]
    combo = get_combined_style(style_keys)
    if combo:
        return combo["name"], combo["description"]
    # Fallback for an unmapped combination (shouldn't happen with 4 known styles).
    label = " + ".join(STYLE_LABELS[k] for k in style_keys)
    return label, "A blend of: " + ", ".join(STYLE_DESCRIPTIONS[k] for k in style_keys)


def pick_color(style_keys: List[str]) -> str:
    """Returns the style key itself (media.py keys its outline colors by
    style name), or "combined" when 2+ styles are blended."""
    if len(style_keys) == 1:
        return style_keys[0]
    return "combined"
