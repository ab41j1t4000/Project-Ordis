from pydantic import BaseModel, Field
from typing import Dict, Any, Literal, Optional
import uuid

EntityType = Literal["person", "project", "file", "task", "place"]

class Entity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EntityType
    name: str
    meta: Optional[Dict[str, Any]] = None