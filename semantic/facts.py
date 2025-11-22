from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class Fact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    evidence_ids: Optional[List[int]] = None