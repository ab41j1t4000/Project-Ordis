from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Literal, Optional

EventType = Literal["chat", "file", "system"]

class Event(BaseModel):
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    event_type: EventType
    source: str                      # "operator", "inbox_scan", "system"
    payload: Dict[str, Any]          # raw content
    meta: Optional[Dict[str, Any]] = None