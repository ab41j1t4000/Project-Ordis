from pathlib import Path
from typing import List
from .events import Event

INBOX_DIR = Path(__file__).parent / "inbox"
PROCESSED_DIR = INBOX_DIR / "processed"
SUPPORTED_EXT = {".md", ".txt"}

# Ensure folders exist
INBOX_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def scan_inbox() -> List[Event]:
    events: List[Event] = []
    for p in INBOX_DIR.glob("*"):
        if p.suffix.lower() not in SUPPORTED_EXT:
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")
        events.append(
            Event(
                event_type="file",
                source="inbox_scan",
                payload={"path": str(p), "name": p.name, "content": text},
                meta={"ext": p.suffix.lower()},
            )
        )

        # Mark as processed to avoid re‑ingest on next scan
        dest = PROCESSED_DIR / p.name
        try:
            p.replace(dest)
        except Exception:
            # If move fails, fall back to leaving it in place
            pass
    return events
