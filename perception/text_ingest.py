from .events import Event

def ingest_chat(text: str, user_id: str = "operator") -> Event:
    return Event(
        event_type="chat",
        source=user_id,
        payload={"text": text},
        meta={"channel": "cli"}
    )