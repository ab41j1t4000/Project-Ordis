# world/_smoke_test.py
from world.model import WorldModel
from world.entities import Entity
from world.relations import Relation

wm = WorldModel()

project_id = wm.add_entity(Entity(type="project", name="Project-Ordis"))
operator_id = wm.add_entity(Entity(type="person", name="operator"))
file_id = wm.add_entity(Entity(type="file", name="test.txt", meta={"path": "perception/inbox/test.txt"}))

wm.add_relation(Relation(type="owned_by", src=file_id, dst=project_id))
wm.add_relation(Relation(type="mentions", src=file_id, dst=operator_id))

wm.save()

wm2 = WorldModel.load()

print("Entities:", len(wm2.entities))
print("Relations:", len(wm2.relations))
print([e.name for e in wm2.find_entities(type="project")])