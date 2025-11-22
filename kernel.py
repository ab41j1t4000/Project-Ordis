from pydantic import BaseModel
import sqlite3
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from world.model import WorldModel
from world.update_rules import apply_event

IDENTITY_PATH = Path(__file__).parent / "identity.yaml"
EPISODIC_DB_PATH = Path(__file__).parent / "memory" / "episodic.db"


class Identity(BaseModel):
    name: str
    purpose: str
    version: str


class Kernel:
    def __init__(self):
        self.identity = self._load_identity()
        self.conn = self._init_episodic_db()
        self.world = WorldModel.load()

    def _load_identity(self) -> Identity:
        with open(IDENTITY_PATH, "r") as f:
            data = yaml.safe_load(f)
        return Identity(**data)

    def _init_episodic_db(self):
        conn = sqlite3.connect(EPISODIC_DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        conn.commit()
        return conn

    def log_episode(self, event_type: str, payload: Dict[str, Any]):
        ts = datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO episodes (ts, event_type, payload) VALUES (?, ?, ?)",
            (ts, event_type, str(payload)),
        )
        self.conn.commit()

    def step(self):
        # Week-1: deterministic step, no intelligence.
        self.log_episode("tick", {"msg": "heartbeat"})
        print(f"[{self.identity.name}] tick")

    def shutdown(self):
        self.conn.close()
    
    def ingest_event(self, event):
        """
        Store any perception Event into episodic memory.
        """
        payload = event.model_dump() if hasattr(event, "model_dump") else event.__dict__
        self.log_episode(event.event_type, payload)
        notes = apply_event(self.world, event)
        if notes:
            self.log_episode("world_update", {"notes": notes})
            self.world.save()