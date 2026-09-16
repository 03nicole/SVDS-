"""Pure plate-text and dedup logic for the SVDS camera node, kept free of
heavy CV/ML imports (cv2, torch, ultralytics, easyocr) so it can be unit
tested without a GPU environment installed.
"""
import difflib
import os
import re

# Zambian plates look like "BAA 1234" — three letters, four digits, no spaces
# once cleaned. Loose on purpose since OCR on a phone feed is noisy.
PLATE_PATTERN = re.compile(r"[A-Z0-9]{5,8}")

# A stationary/slow vehicle gets re-read every processed frame, and OCR noise
# means the exact string drifts (ALX3665 / ALK3665 / AL3065 / ...). An exact
# cooldown key lets every variant bypass the cooldown, so instead we compare
# each new reading against still-active recent readings by similarity.
DEDUP_SIMILARITY_THRESHOLD = float(os.getenv("DEDUP_SIMILARITY_THRESHOLD", "0.75"))


def clean_plate_text(raw: str) -> str | None:
    text = re.sub(r"[^A-Z0-9]", "", raw.upper())
    return text if PLATE_PATTERN.fullmatch(text) else None


def is_recent_duplicate(
    recent_sightings: list[tuple[str, float]],
    plate: str,
    now: float,
    cooldown_seconds: float,
    similarity_threshold: float = DEDUP_SIMILARITY_THRESHOLD,
) -> bool:
    """True if `plate` is a fuzzy match for any reading still inside its
    cooldown window. Mutates `recent_sightings` in place to drop expired
    entries so the list doesn't grow forever."""
    recent_sightings[:] = [
        (p, t) for p, t in recent_sightings if now - t <= cooldown_seconds
    ]
    return any(
        difflib.SequenceMatcher(None, plate, p).ratio() >= similarity_threshold
        for p, _ in recent_sightings
    )
