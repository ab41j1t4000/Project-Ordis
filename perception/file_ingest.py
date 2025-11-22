from pathlib import Path
from typing import List
from .events import Event

INBOX_DIR = Path(__file__).parent / "inbox"
SUPPORTED_EXT = {".md", ".txt"}

def scan_inbox() -> List[Event]:
    events: List[Event] = []
    for p in INBOX_DIR.glob("*"):
        if p.suffix.lower() not in SUPPORTED_EXT:
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")
        events.append(Event(
            event_type="file",
            source="inbox_scan",
            payload={
                "path": str(p),
                "name": p.name,
                "content": text
            },
            meta={"ext": p.suffix.lower()}
        ))
    return events