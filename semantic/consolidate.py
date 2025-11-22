from typing import List
from semantic.memory import SemanticMemory
from semantic.facts import Fact
from world.model import WorldModel


def _upsert(sm: SemanticMemory, fact: Fact) -> str:
    existing = sm.find_facts(
        subject=fact.subject,
        predicate=fact.predicate,
        object=fact.object
    )

    if existing:
        f = existing[0]
        f.confidence = max(f.confidence, fact.confidence)
        return f.id

    return sm.add_fact(fact)


def consolidate(wm: WorldModel, sm: SemanticMemory) -> List[str]:
    notes: List[str] = []

    # Persons
    for p in wm.find_entities(type="person"):
        _upsert(sm, Fact(subject=p.id, predicate="is_a", object="person"))
        notes.append(f"fact: {p.name} is_a person")

    # Files + part_of Project-Ordis
    projects = wm.find_entities(type="project", name="Project-Ordis")
    project_id = projects[0].id if projects else None

    for f in wm.find_entities(type="file"):
        _upsert(sm, Fact(subject=f.id, predicate="is_a", object="file"))
        notes.append(f"fact: {f.name} is_a file")

        if project_id:
            _upsert(sm, Fact(subject=f.id, predicate="part_of", object=project_id))
            notes.append(f"fact: {f.name} part_of Project-Ordis")

    return notes