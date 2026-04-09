from pydantic import BaseModel
from typing import List

# OLD (optional)
class NewsInput(BaseModel):
    text: str

# NEW (REQUIRED 🔥)
class ClaimRequest(BaseModel):
    claim_id: int
    perceptions: List[str]