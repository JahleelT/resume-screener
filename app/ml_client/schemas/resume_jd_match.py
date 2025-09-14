from pydantic import BaseModel
from typing import List

class ResumeJDMatch(BaseModel):
  match_score: float
  matched_skills: List[str]
  missing_skills: List[str]
  summary: str