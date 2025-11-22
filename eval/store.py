import json
from pathlib import Path
from typing import Dict, List
from .records import EvalRecord

EVAL_STATE_PATH = Path(__file__).parent / "eval_state.json"

class EvalStore:
    def __init__(self):
        self.records: Dict[str, EvalRecord] = {}

    def add_record(self, r: EvalRecord) -> str:
        self.records[r.id] = r
        return r.id

    def list_records(self) -> List[EvalRecord]:
        return list(self.records.values())

    def save(self):
        data = [
            r.model_dump() if hasattr(r, "model_dump") else r.dict()
            for r in self.records.values()
        ]
        EVAL_STATE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls):
        es = cls()
        if not EVAL_STATE_PATH.exists():
            return es
        data = json.loads(EVAL_STATE_PATH.read_text(encoding="utf-8"))
        for d in data:
            r = EvalRecord(**d)
            es.records[r.id] = r
        return es