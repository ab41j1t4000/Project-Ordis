from typing import List
from .records import EvalRecord
from world.model import WorldModel
from memory.semantic.memory import SemanticMemory


def run_coherence_eval(wm: WorldModel, sm: SemanticMemory) -> EvalRecord:
    notes: List[str] = []
    total = 0
    passed = 0

    # find Project-Ordis id if present
    proj = wm.find_entities(type="project", name="Project-Ordis")
    project_id = proj[0].id if proj else None

    # persons must have is_a person
    for p in wm.find_entities(type="person"):
        total += 1
        ok = bool(sm.find_facts(subject=p.id, predicate="is_a", object="person"))
        if ok:
            passed += 1
        else:
            notes.append(f"missing fact: {p.name} is_a person")

    # files must have is_a file
    for f in wm.find_entities(type="file"):
        total += 1
        ok = bool(sm.find_facts(subject=f.id, predicate="is_a", object="file"))
        if ok:
            passed += 1
        else:
            notes.append(f"missing fact: {f.name} is_a file")

        # files must be part_of Project-Ordis
        if project_id:
            total += 1
            ok2 = bool(
                sm.find_facts(subject=f.id, predicate="part_of", object=project_id)
            )
            if ok2:
                passed += 1
            else:
                notes.append(f"missing fact: {f.name} part_of Project-Ordis")

    score = (passed / total) if total > 0 else 1.0

    return EvalRecord(eval_type="coherence_v0", score=score, notes=notes)
