from pydantic import BaseModel
from typing import List

class AnalysisResult(BaseModel):
  match_score: float = Field(..., description = "Fit score between 0 and 1 indicating how well the resume matches the JD")
  matched_skills: List[str] = Field(..., description = "Skills explicitly present in both the resume and the JD")
  missing_skills: List[str] = Field(..., description = "Skills explicitly present in the JD, but missing in the resume")
  strengths: List[str] = Field(..., description = "Key strengths of the candidate relevant to the JD")
  weaknesses: List[str] = Field(..., description = "Gaps or shortcomings of the candidate compared to the JD")