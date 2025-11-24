from pydantic import BaseModel, Field
import sqlite3
import yaml
from pathlib import Path
from datetime import datetime
import json
from typing import Any, Dict, List, Optional, Callable
from world.model import WorldModel
from world.update_rules import apply_event
from eval.store import EvalStore
from eval.coherence import run_coherence_eval
from memory.semantic.memory import SemanticMemory
from memory.semantic.consolidate import consolidate

IDENTITY_PATH = Path(__file__).parent.parent / "identity" / "identity.yaml"
EPISODIC_DB_PATH = Path(__file__).parent.parent / "memory" / "episodic.db"
SELF_STATE_PATH = Path(__file__).parent.parent / "memory" / "self_state.json"
GOALS_DB_PATH = Path(__file__).parent.parent / "memory" / "goals.db"

# Homeostasis v0: if coherence drops below this, enter SAFE_MODE
HOMEOSTASIS_MIN_COHERENCE = 0.6
# Homeostasis v1: below this (but above min), pause active goal to reduce load
HOMEOSTASIS_WARN_COHERENCE = 0.75
# If coherence rises back above this, resume highest‑priority paused goal
HOMEOSTASIS_RESUME_COHERENCE = 0.85

# Deterministic goal handler signature (v1: handlers may emit events)
GoalHandler = Callable[["Kernel"], Optional[Any]]


class Identity(BaseModel):
    name: str
    purpose: str
    version: str


class SelfState(BaseModel):
    """Mutable, persistent runtime self-state (storage only)."""

    mode: str = "idle"  # idle | ingesting | consolidating | evaluating | safe_mode
    safe_mode: bool = False
    last_tick_ts: Optional[str] = None
    last_event_ts: Optional[str] = None
    last_event_type: Optional[str] = None
    active_goal_id: Optional[str] = None
    notes: Dict[str, Any] = {}


# Goal Execution v1: deterministic event emitted by a goal handler.
class GoalEvent(BaseModel):
    """Deterministic event emitted by a goal handler."""

    event_type: str = "goal"
    source: str = "goal_exec"
    payload: Dict[str, Any]
    ts: str = Field(default_factory=lambda: datetime.now().astimezone().isoformat())
    meta: Optional[Dict[str, Any]] = None


class Kernel:
    def __init__(self):
        self.identity = self._load_identity()
        self.conn = self._init_episodic_db()
        self.goals_conn = self._init_goals_db()
        self.world = WorldModel.load()
        self.semantic = SemanticMemory.load()
        self.eval_store = EvalStore.load()
        self._event_queue: List[Any] = []
        self.safe_mode: bool = False
        self.self_state = self._load_self_state()
        # keep safe_mode flags in sync
        self.safe_mode = self.self_state.safe_mode
        # Goal execution v0: deterministic handlers (no intelligence)
        self.goal_handlers: Dict[str, GoalHandler] = {}

    def _load_identity(self) -> Identity:
        with open(IDENTITY_PATH, "r") as f:
            data = yaml.safe_load(f)
        return Identity(**data)

    def _load_self_state(self) -> SelfState:
        if not SELF_STATE_PATH.exists():
            ss = SelfState()
            SELF_STATE_PATH.write_text(ss.model_dump_json(indent=2), encoding="utf-8")
            return ss
        data = json.loads(SELF_STATE_PATH.read_text(encoding="utf-8"))
        return SelfState(**data)

    def _save_self_state(self):
        # mirror kernel flag
        self.self_state.safe_mode = self.safe_mode
        SELF_STATE_PATH.write_text(
            self.self_state.model_dump_json(indent=2), encoding="utf-8"
        )

    def _init_episodic_db(self):
        conn = sqlite3.connect(EPISODIC_DB_PATH)
        cur = conn.cursor()

        # Ensure base table exists (old or new schema)
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

        # --- schema migration: add payload_json if missing ---
        cur.execute("PRAGMA table_info(episodes)")
        cols = [row[1] for row in cur.fetchall()]
        if "payload_json" not in cols:
            cur.execute("ALTER TABLE episodes ADD COLUMN payload_json TEXT")
            conn.commit()

            # Backfill payload_json from legacy payload column if it exists
            if "payload" in cols:
                cur.execute(
                    "UPDATE episodes SET payload_json = payload WHERE payload_json IS NULL"
                )
                conn.commit()

        return conn

    def _init_goals_db(self):
        conn = sqlite3.connect(GOALS_DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active',
                created_ts TEXT NOT NULL,
                updated_ts TEXT NOT NULL,
                meta_json TEXT
            )
            """
        )
        conn.commit()
        return conn

    def log_episode(self, event_type: str, payload: Dict[str, Any]):
        ts = datetime.utcnow().isoformat()
        payload_json = json.dumps(payload, ensure_ascii=False)
        # Legacy column kept for backward compatibility / NOT NULL constraint
        legacy_payload = payload_json
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO episodes (ts, event_type, payload, payload_json) VALUES (?, ?, ?, ?)",
            (ts, event_type, legacy_payload, payload_json),
        )
        self.conn.commit()

    def enqueue_event(self, event: Any):
        """Stage a perception event to be processed on the next tick."""
        self._event_queue.append(event)

    def ingest_event(self, event: Any):
        """Record an event and queue it for deterministic processing on tick."""
        payload = event.model_dump() if hasattr(event, "model_dump") else event.__dict__
        # Log raw event
        self.log_episode(event.event_type, payload)
        # Stage for tick-time processing
        self.enqueue_event(event)

    def emit_goal_event(
        self, payload: Dict[str, Any], meta: Optional[Dict[str, Any]] = None
    ):
        """Goals emit events; kernel ingests them like perception."""
        ev = GoalEvent(payload=payload, meta=meta)
        self.ingest_event(ev)

    def _process_event_queue(self) -> List[str]:
        """Apply all queued events to the world in-order. Returns world-update notes."""
        notes: List[str] = []
        while self._event_queue:
            ev = self._event_queue.pop(0)
            # update self-state about last event
            self.self_state.last_event_ts = getattr(
                ev, "ts", datetime.utcnow().isoformat()
            )
            self.self_state.last_event_type = getattr(
                ev, "event_type", type(ev).__name__
            )
            try:
                ev_notes = apply_event(self.world, ev) or []
                if ev_notes:
                    notes.extend(ev_notes)
            except Exception as e:
                # Enter safe mode on world update failure
                self.safe_mode = True
                self.log_episode(
                    "kernel_error",
                    {
                        "phase": "apply_event",
                        "error": str(e),
                        "event_type": getattr(ev, "event_type", type(ev).__name__),
                    },
                )
        if notes:
            self.world.save()
            self.log_episode("world_update", {"notes": notes})
        return notes

    def add_goal(
        self,
        goal_id: str,
        description: str,
        priority: int = 0,
        meta: Optional[Dict[str, Any]] = None,
    ):
        """Create or update a goal (storage only)."""
        now = datetime.utcnow().isoformat()
        meta_json = json.dumps(meta or {}, ensure_ascii=False)
        cur = self.goals_conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO goals
            (id, description, priority, status, created_ts, updated_ts, meta_json)
            VALUES (
                ?, ?, ?,
                COALESCE((SELECT status FROM goals WHERE id=?), 'active'),
                COALESCE((SELECT created_ts FROM goals WHERE id=?), ?),
                ?, ?
            )
            """,
            (goal_id, description, priority, goal_id, goal_id, now, now, meta_json),
        )
        self.goals_conn.commit()
        self.self_state.active_goal_id = goal_id
        self._save_self_state()
        self.log_episode(
            "goal_added",
            {"id": goal_id, "description": description, "priority": priority},
        )

    def update_goal_status(self, goal_id: str, status: str):
        """Update goal status. status ∈ {'active','paused','done','dropped'}"""
        now = datetime.utcnow().isoformat()
        cur = self.goals_conn.cursor()
        cur.execute(
            "UPDATE goals SET status=?, updated_ts=? WHERE id=?",
            (status, now, goal_id),
        )
        self.goals_conn.commit()
        self.log_episode("goal_status", {"id": goal_id, "status": status})

    def set_active_goal(self, goal_id: Optional[str]):
        """Deterministically set the currently active goal id."""
        self.self_state.active_goal_id = goal_id
        self._save_self_state()
        self.log_episode("active_goal_set", {"goal_id": goal_id})

    def register_goal_handler(self, goal_id: str, handler: GoalHandler):
        """Register a deterministic handler for a specific goal id."""
        self.goal_handlers[goal_id] = handler
        self.log_episode("goal_handler_registered", {"goal_id": goal_id})

    def run_active_goal(self):
        """Execute the active goal handler once per tick; handlers emit events."""
        gid = self.self_state.active_goal_id
        if not gid:
            return

        handler = self.goal_handlers.get(gid)
        if handler is None:
            self.log_episode("goal_no_handler", {"goal_id": gid})
            return

        try:
            self.self_state.mode = "goal_exec"
            out = handler(self)

            # Normalize handler output into ingestion events
            if out is None:
                pass
            elif isinstance(out, list):
                for ev in out:
                    self.ingest_event(ev)
            else:
                self.ingest_event(out)

            self.log_episode("goal_exec", {"goal_id": gid})
        except Exception as e:
            self.safe_mode = True
            self.log_episode(
                "kernel_error",
                {"phase": "goal_exec", "goal_id": gid, "error": str(e)},
            )

    def list_goals(self, status: Optional[str] = None):
        """List goals, optionally filtered by status, ordered by priority desc."""
        cur = self.goals_conn.cursor()
        if status:
            rows = cur.execute(
                "SELECT id, description, priority, status, created_ts, updated_ts, meta_json FROM goals WHERE status=? ORDER BY priority DESC",
                (status,),
            ).fetchall()
        else:
            rows = cur.execute(
                "SELECT id, description, priority, status, created_ts, updated_ts, meta_json FROM goals ORDER BY priority DESC"
            ).fetchall()
        return rows

    def list_active_goals_lowest_first(self):
        """Return active goals ordered by priority ascending (lowest first)."""
        cur = self.goals_conn.cursor()
        rows = cur.execute(
            "SELECT id, description, priority, status, created_ts, updated_ts, meta_json FROM goals WHERE status='active' ORDER BY priority ASC"
        ).fetchall()
        return rows

    def list_paused_goals_highest_first(self):
        """Return paused goals ordered by priority descending (highest first)."""
        cur = self.goals_conn.cursor()
        rows = cur.execute(
            "SELECT id, description, priority, status, created_ts, updated_ts, meta_json FROM goals WHERE status='paused' ORDER BY priority DESC"
        ).fetchall()
        return rows

    def step(self):
        """One deterministic tick. No intelligence; just plumbing + self-state."""
        now_ts = datetime.utcnow().isoformat()

        # 0) heartbeat
        self.self_state.mode = "idle" if not self.safe_mode else "safe_mode"
        self.self_state.last_tick_ts = now_ts
        self.log_episode("tick", {"msg": "heartbeat", "safe_mode": self.safe_mode})
        print(f"[{self.identity.name}] tick")

        # 1) apply queued perception -> world
        if self._event_queue:
            self.self_state.mode = "ingesting"
        self._process_event_queue()

        # 2) consolidate world -> semantic (skip if in safe mode)
        if not self.safe_mode:
            self.self_state.mode = "consolidating"
            try:
                self.run_consolidation()
            except Exception as e:
                self.safe_mode = True
                self.log_episode(
                    "kernel_error", {"phase": "consolidate", "error": str(e)}
                )

        # 3) eval current state (skip if in safe mode)
        eval_record = None
        if not self.safe_mode:
            self.self_state.mode = "evaluating"
            try:
                eval_record = self.run_eval()
            except Exception as e:
                self.safe_mode = True
                self.log_episode("kernel_error", {"phase": "eval", "error": str(e)})

        # 3.5) homeostasis reacts to eval deterministically
        if not self.safe_mode:
            try:
                self.run_homeostasis(eval_record)
            except Exception as e:
                self.safe_mode = True
                self.log_episode(
                    "kernel_error", {"phase": "homeostasis", "error": str(e)}
                )

        # 3.8) execute active goal deterministically (v0)
        if not self.safe_mode:
            self.run_active_goal()

        # 4) safe-mode behavior: stay minimal until external reset
        if self.safe_mode:
            self.self_state.mode = "safe_mode"
            print(f"[{self.identity.name}] SAFE_MODE")

        # 5) persist self-state snapshot
        self._save_self_state()

    def shutdown(self):
        try:
            self.conn.close()
        finally:
            self.goals_conn.close()

    def run_consolidation(self):
        notes = consolidate(self.world, self.semantic)
        if notes:
            self.semantic.save()
            self.log_episode("semantic_update", {"notes": notes})

    def run_eval(self):
        r = run_coherence_eval(self.world, self.semantic)
        self.eval_store.add_record(r)
        self.eval_store.save()
        self.log_episode(
            "eval", {"type": r.eval_type, "score": r.score, "notes": r.notes}
        )
        return r

    def run_homeostasis(self, eval_record):
        """Homeostasis v1: react to eval deterministically. No planning."""
        if eval_record is None:
            return

        score = getattr(eval_record, "score", None)
        eval_type = getattr(eval_record, "eval_type", "coherence")
        notes = getattr(eval_record, "notes", None)
        now_ts = datetime.utcnow().isoformat()

        # Persist last eval snapshot into self-state
        self.self_state.notes["last_eval"] = {
            "type": eval_type,
            "score": score,
            "notes": notes,
            "ts": now_ts,
        }

        # Explicit coherence/entropy fields (karma = entropy)
        self.self_state.notes["coherence"] = score
        self.self_state.notes["entropy"] = None if score is None else (1 - score)

        if isinstance(score, (int, float)):
            # If coherence is too low, enter SAFE_MODE
            if score < HOMEOSTASIS_MIN_COHERENCE:
                self.safe_mode = True
                self.log_episode(
                    "homeostasis_trigger",
                    {
                        "reason": "low_coherence",
                        "score": score,
                        "threshold": HOMEOSTASIS_MIN_COHERENCE,
                    },
                )

            # Warning band: pause lowest-priority active goals first to reduce load
            elif score < HOMEOSTASIS_WARN_COHERENCE:
                active_goals = self.list_active_goals_lowest_first()
                paused_ids = []
                for row in active_goals:
                    goal_id = row[0]
                    self.update_goal_status(goal_id, "paused")
                    paused_ids.append(goal_id)
                    # Pause at most 1 goal per tick in v1
                    break

                if paused_ids:
                    # If the paused goal was the active one, clear active_goal_id
                    if self.self_state.active_goal_id in paused_ids:
                        self.self_state.active_goal_id = None
                        self._save_self_state()
                    self.log_episode(
                        "homeostasis_goal_pause",
                        {"paused_goals": paused_ids, "score": score},
                    )
            else:
                # Stable band: if no active goal, resume highest‑priority paused goal
                if (
                    score >= HOMEOSTASIS_RESUME_COHERENCE
                    and not self.self_state.active_goal_id
                ):
                    paused = self.list_paused_goals_highest_first()
                    if paused:
                        resume_id = paused[0][0]
                        self.update_goal_status(resume_id, "active")
                        self.set_active_goal(resume_id)
                        self.log_episode(
                            "homeostasis_goal_resume",
                            {"goal_id": resume_id, "score": score},
                        )

    def reset_safe_mode(self, reason: str = "manual_reset"):
        """Deterministically exit SAFE_MODE after an external fix."""
        self.safe_mode = False
        self.self_state.safe_mode = False
        self.self_state.mode = "idle"
        self.log_episode("safe_mode_reset", {"reason": reason})
        self._save_self_state()


def main(max_ticks: int = 5):
    """
    Kernel-owned entrypoint.
    Creates Ordis, runs deterministic ticks, then shuts down cleanly.
    """
    k = Kernel()
    try:
        from kernel.tick import run_tick_loop

        run_tick_loop(k.step, max_ticks=max_ticks)
    finally:
        k.shutdown()


if __name__ == "__main__":
    main()
