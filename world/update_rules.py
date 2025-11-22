from typing import List
from world.model import WorldModel
from world.entities import Entity
from world.relations import Relation
from perception.events import Event

def apply_event(wm: WorldModel, event: Event) -> List[str]:
    """
    Deterministic rules: take an Event and update world model.
    Returns list of update notes (for logging/debug).
    """
    notes: List[str] = []

    # Ensure Project-Ordis exists
    projects = wm.find_entities(type="project", name="Project-Ordis")
    if projects:
        project = projects[0]
    else:
        project_id = wm.add_entity(Entity(type="project", name="Project-Ordis"))
        project = wm.entities[project_id]
        notes.append("created project: Project-Ordis")

    # Rule: chat event implies operator person exists
    if event.event_type == "chat":
        persons = wm.find_entities(type="person", name=event.source)
        if not persons:
            pid = wm.add_entity(Entity(type="person", name=event.source))
            notes.append(f"created person: {event.source}")
        return notes

    # Rule: file event creates/updates File entity and links to Project-Ordis
    if event.event_type == "file":
        file_name = event.payload.get("name", "unknown_file")
        file_path = event.payload.get("path")

        existing = wm.find_entities(type="file", name=file_name)
        if existing:
            f_ent = existing[0]
            # update meta deterministically
            meta = f_ent.meta or {}
            if file_path:
                meta["path"] = file_path
            f_ent.meta = meta
            notes.append(f"updated file: {file_name}")
        else:
            fid = wm.add_entity(Entity(
                type="file",
                name=file_name,
                meta={"path": file_path} if file_path else None
            ))
            f_ent = wm.entities[fid]
            notes.append(f"created file: {file_name}")

        # link file -> project
        wm.add_relation(Relation(
            type="part_of",
            src=f_ent.id,
            dst=project.id,
            confidence=1.0
        ))
        notes.append(f"linked file '{file_name}' -> Project-Ordis")

    return notes