import json
from pathlib import Path
from typing import Dict, List, Optional
from .entities import Entity, EntityType
from .relations import Relation, RelationType

WORLD_STATE_PATH = Path(__file__).parent / "world_state.json"

class WorldModel:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}

    # ---- entities ----
    def add_entity(self, e: Entity) -> str:
        self.entities[e.id] = e
        return e.id

    def find_entities(
        self, 
        type: Optional[EntityType] = None, 
        name: Optional[str] = None
    ) -> List[Entity]:
        out = list(self.entities.values())
        if type:
            out = [e for e in out if e.type == type]
        if name:
            out = [e for e in out if e.name == name]
        return out

    # ---- relations ----
    def add_relation(self, r: Relation) -> str:
        self.relations[r.id] = r
        return r.id

    def find_relations(
        self, 
        type: Optional[RelationType] = None
    ) -> List[Relation]:
        out = list(self.relations.values())
        if type:
            out = [r for r in out if r.type == type]
        return out

    # ---- persistence ----
    def save(self):
        data = {
            "entities": [e.model_dump() for e in self.entities.values()],
            "relations": [r.model_dump() for r in self.relations.values()],
        }
        WORLD_STATE_PATH.write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls):
        wm = cls()
        if not WORLD_STATE_PATH.exists():
            return wm

        data = json.loads(WORLD_STATE_PATH.read_text(encoding="utf-8"))
        for e in data.get("entities", []):
            ent = Entity(**e)
            wm.entities[ent.id] = ent
        for r in data.get("relations", []):
            rel = Relation(**r)
            wm.relations[rel.id] = rel

        return wm