import json
from pathlib import Path
from typing import Dict, List, Optional
from .facts import Fact

SEMANTIC_STATE_PATH = Path(__file__).parent / "semantic_state.json"

class SemanticMemory:
    def __init__(self):
        self.facts: Dict[str, Fact] = {}

    def add_fact(self, f: Fact) -> str:
        self.facts[f.id] = f
        return f.id

    def find_facts(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object: Optional[str] = None
    ) -> List[Fact]:
        out = list(self.facts.values())
        if subject:
            out = [x for x in out if x.subject == subject]
        if predicate:
            out = [x for x in out if x.predicate == predicate]
        if object:
            out = [x for x in out if x.object == object]
        return out

    def save(self):
        data = [
            f.model_dump() if hasattr(f, "model_dump") else f.dict()
            for f in self.facts.values()
        ]
        SEMANTIC_STATE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls):
        sm = cls()
        if not SEMANTIC_STATE_PATH.exists():
            return sm
        raw = json.loads(SEMANTIC_STATE_PATH.read_text(encoding="utf-8"))
        for d in raw:
            f = Fact(**d)
            sm.facts[f.id] = f
        return sm