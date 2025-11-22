from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class EvalRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    eval_type: str
    score: float
    notes: List[str] = []
    evidence_ids: Optional[List[int]] = None