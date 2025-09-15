from pydantic import BaseModel
from typing import List

class WriterOutput(BaseModel): 
  summary: str = Field(..., description = "A human-readable 3-5 sentence summary of how well the candidate matches the JD")
  recommendations: str = Field(..., description = "Specific, actionable suggestions for improving the resume to better match the JD")
  overall_rating: str = Field(..., description = "A plain-language rating such as 'Strong Match', 'Moderate Match', 'Weak Match'")