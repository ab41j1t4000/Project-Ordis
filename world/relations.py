from pydantic import BaseModel, Field
from typing import Literal, Optional
import uuid

RelationType = Literal[
    "owned_by", "part_of", "mentions", "linked_to", "authored_by"
]

class Relation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: RelationType
    src: str          # entity id
    dst: str          # entity id
    confidence: float = 1.0
    note: Optional[str] = None